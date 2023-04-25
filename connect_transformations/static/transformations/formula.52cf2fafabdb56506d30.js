/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 506:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {

"use strict";

// UNUSED EXPORTS: createFormulaRow, formula

// EXTERNAL MODULE: ./node_modules/suggest-box/index.js
var suggest_box = __webpack_require__(764);
var suggest_box_default = /*#__PURE__*/__webpack_require__.n(suggest_box);
// EXTERNAL MODULE: ./node_modules/@cloudblueconnect/connect-ui-toolkit/dist/index.js
var dist = __webpack_require__(164);
;// CONCATENATED MODULE: ./ui/src/utils.js

/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
const validate = (functionName, data) => fetch(`/api/validate/${functionName}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

const getLookupSubscriptionCriteria = () => fetch('/api/lookup_subscription/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getLookupProductItemCriteria = () => fetch('/api/lookup_product_item/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getLookupSubscriptionParameters = (productId) => fetch(`/api/lookup_subscription/parameters?product_id=${productId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getCurrencies = () => fetch('/api/currency_conversion/currencies').then(response => response.json());

/* The data should contain pattern (and optionally groups) keys.
We expect the return groups key (with the new keys found in the regex) and the order
 (to display in order on the UI) */
const getGroups = (data) => fetch('/api/split_column/extract_groups', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());


/* The data should contain list of jq expressions and all input columns.
We expect to return columns used in expressions */
const getJQInput = (data) => fetch('/api/formula/extract_input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

;// CONCATENATED MODULE: ./ui/src/components.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/

// render UI components - show/hide
const showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

const hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};

const showError = (message) => {
  const oldError = document.getElementById('error');
  if (oldError) {
    oldError.remove();
  }
  const error = document.createElement('div');
  error.id = 'error';
  error.innerHTML = `<div class="c-alert">${message}</div>`;
  document.getElementsByTagName('body')[0].appendChild(error);
  document.getElementById('error').scrollIntoView();
};

const hideError = () => {
  const error = document.getElementById('error');
  if (error) {
    error.remove();
  }
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/formula.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









let suggestor = {};

const createFormulaRow = (parent, index, output, formula, columnId) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <input type="text" placeholder="Output column" style="width: 70%;" ${output ? `value="${output}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
      <div class="input-group _mt_12 _mb_18">
          <label class="label" for="${columnId || `formula-${index}`}">Formula:</label>
          <textarea materialize id="${columnId || `formula-${index}`}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
      </div>
    `;
  parent.appendChild(item);
  suggest_box_default()(document.getElementById(`${columnId || `formula-${index}`}`), suggestor);
  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      showError('You need to have at least one row');
    } else {
      document.getElementById(`wrapper-${index}`).remove();
      const buttons = document.getElementsByClassName('delete-button');
      if (buttons.length === 1) {
        buttons[0].disabled = true;
      }
    }
  });
  const buttons = document.getElementsByClassName('delete-button');
  for (let i = 0; i < buttons.length; i += 1) {
    if (buttons.length === 1) {
      buttons[i].disabled = true;
    } else {
      buttons[i].disabled = false;
    }
  }
};

const formula = (app) => {
  if (!app) return;

  hideComponent('loader');
  showComponent('app');

  let rowIndex = 0;
  let columns = [];
  let columnId = '';

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;
    suggestor = { '.': availableColumns.map(col => ({
      title: col.name,
      value: `."${col.name}"`,
    })) };

    const content = document.getElementById('content');
    if (settings && settings.expressions) {
      settings.expressions.forEach((expression, i) => {
        rowIndex = i;
        columnId = columns.find(col => col.name === expression.to).id;
        createFormulaRow(content, rowIndex, expression.to, expression.formula, columnId);
      });
    } else {
      createFormulaRow(content, rowIndex);
    }
    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createFormulaRow(content, rowIndex);
    });
  });

  app.listen('save', async () => {
    const data = {
      settings: { expressions: [] },
      columns: {
        input: columns,
        output: [],
      },
    };
    const form = document.getElementsByClassName('list-wrapper');
    // eslint-disable-next-line no-restricted-syntax
    for (const line of form) {
      const to = line.getElementsByTagName('input')[0].value;
      const jqFormula = line.getElementsByTagName('textarea')[0].value;
      const jqColumn = line.getElementsByTagName('textarea')[0].id;

      const outputColumn = {
        name: to,
        type: 'string',
        nullable: true,
      };
      if (!jqColumn.startsWith('formula-')) {
        outputColumn.id = jqColumn;
      }
      const expression = {
        to,
        formula: jqFormula,
      };
      data.settings.expressions.push(expression);
      data.columns.output.push(outputColumn);
    }

    try {
      const overview = await validate('formula', data);
      if (overview.error) {
        throw new Error(overview.error);
      } else {
        const inputColumns = await getJQInput({
          expressions: data.settings.expressions,
          columns,
        });
        if (inputColumns.error) {
          throw new Error(inputColumns.error);
        } else {
          data.columns.input = inputColumns;
        }
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(formula);


/***/ }),

/***/ 933:
/***/ (() => {

/* (ignored) */

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			2: 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkeaas_e2e_transformations_mock"] = self["webpackChunkeaas_e2e_transformations_mock"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(506)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;