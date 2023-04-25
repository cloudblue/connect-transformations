/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 118:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {


// UNUSED EXPORTS: createGroupRows, splitColumn

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

;// CONCATENATED MODULE: ./ui/src/pages/transformations/split_column.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









function getCurrentGroups(parent) {
  const descendents = parent.getElementsByTagName('input');
  const currentGroups = {};
  for (let i = 0; i < descendents.length; i += 1) {
    const element = descendents[i];
    const dataType = document.getElementById(`${element.id}-datatype`);
    if (dataType && dataType.value === 'decimal') {
      const precision = document.getElementById(`${element.id}-precision`).value;
      currentGroups[element.id] = {
        name: element.value,
        type: dataType.value,
        precision,
      };
    } else {
      currentGroups[element.id] = { name: element.value, type: dataType.value };
    }
  }

  return currentGroups;
}

function buildSelectColumnType(groupKey) {
  return `
  <select id="${groupKey}-datatype">
  <option value="string" selected>String</option>
  <option value="integer">Integer</option>
  <option value="decimal">Decimal</option>
  <option value="boolean">Boolean</option>
  <option value="datetime">Datetime</option>
  </select>
  `;
}

function buildSelectColumnPrecision(groupKey, enabled) {
  return `
  <select id="${groupKey}-precision" ${enabled === true ? '' : 'disabled'}>
  <option value="2" selected>2 decimals</option>
  <option value="3">3 decimals</option>
  <option value="4">4 decimals</option>
  <option value="5">5 decimals</option>
  <option value="6">6 decimals</option>
  <option value="7">7 decimals</option>
  <option value="8">8 decimals</option>
  </select>
  `;
}

function buildGroups(groups) {
  const parent = document.getElementById('output');
  parent.innerHTML = '';
  if (Object.keys(groups).length > 0) {
    const item = document.createElement('div');
    item.setAttribute('class', 'wrapper output-header');
    item.innerHTML = `
    <div>
    Name
    </div>
    <div>
    Type
    </div>
    <div>
    Precision
    </div>
    `;
    parent.appendChild(item);
  }
  Object.keys(groups).forEach(groupKey => {
    const groupValue = groups[groupKey];
    const item = document.createElement('div');
    item.className = 'wrapper';
    const selectType = buildSelectColumnType(groupKey);
    const selectPrecision = buildSelectColumnPrecision(groupKey, groupValue.type === 'decimal');
    item.innerHTML = `
    <div>
    <input 
    type="text" 
    class="output-input" 
    id="${groupKey}"
    placeholder="${groupKey} group name" 
    value="${groupValue.name}"/>
    </div>
    <div>
    ${selectType}
    </div>
    <div>
    ${selectPrecision}
    </div>
    `;
    parent.appendChild(item);
    document.getElementById(`${groupKey}-datatype`).value = groupValue.type;
    document.getElementById(`${groupKey}-precision`).value = groupValue.precision;
    document.getElementById(`${groupKey}-datatype`).addEventListener('change', () => {
      if (document.getElementById(`${groupKey}-datatype`).value === 'decimal') {
        document.getElementById(`${groupKey}-precision`).disabled = false;
      } else {
        document.getElementById(`${groupKey}-precision`).disabled = true;
      }
    });
  });
}

const createGroupRows = async () => {
  const parent = document.getElementById('output');
  const groups = getCurrentGroups(parent);
  const pattern = document.getElementById('pattern').value;
  if (pattern) {
    const body = { pattern, groups };
    const response = await getGroups(body);
    if (response.error) {
      showError(response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    showError('The regular expression is empty');
  }
};

const splitColumn = (app) => {
  if (!app) return;

  let columns = [];

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    showComponent('loader');
    hideComponent('app');

    columns = availableColumns;

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('pattern').value = settings.regex.pattern;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      buildGroups(settings.regex.groups);
    }

    document.getElementById('refresh').addEventListener('click', () => {
      createGroupRows();
    });
    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', async () => {
    const data = {
      settings: {},
      columns: {
        input: [],
        output: [],
      },
      overview: '',
    };
    showComponent('loader');
    hideComponent('app');

    const inputSelector = document.getElementById('column');
    const selectedColumn = inputSelector.options[inputSelector.selectedIndex].text;
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    data.columns.input.push(inputColumn);

    const selector = document.getElementById('output');
    const options = selector.getElementsByTagName('input');
    for (let i = 0; i < options.length; i += 1) {
      const option = options[i];
      const dataType = document.getElementById(`${option.id}-datatype`).value;
      data.columns.output.push({
        name: option.value,
        type: dataType,
        description: '',
      });
    }

    data.settings = {
      from: selectedColumn,
      regex: {
        pattern: document.getElementById('pattern').value,
        groups: getCurrentGroups(document.getElementById('output')),
      },
    };

    try {
      const overview = await validate('split_column', data);
      if (overview.error) {
        throw new Error(overview.error);
      }

      if (data.columns.output.length === 0) {
        throw new Error('No output columns defined');
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(splitColumn);


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
/******/ 			12: 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(118)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;