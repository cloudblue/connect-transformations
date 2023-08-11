/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 262:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {


// UNUSED EXPORTS: createOutputColumnForLookup, lookupSubscription

// EXTERNAL MODULE: ./node_modules/@cloudblueconnect/connect-ui-toolkit/dist/index.js
var dist = __webpack_require__(164);
;// CONCATENATED MODULE: ./ui/src/utils.js

/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
const validate = (functionName, data) => fetch(`/api/${functionName}/validate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
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

/* The data should contain list of attached files. */
const getAttachments = (streamId) => fetch(`/api/attachment_lookup/${streamId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable */
const getAirtableBases = (key) => fetch(`/api/airtable_lookup/bases?api_key=${key}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable and the base id is the id of the base */
const getAirtableTables = (key, baseId) => fetch(`/api/airtable_lookup/tables?api_key=${key}&base_id=${baseId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getColumnLabel = (column) => {
  const colIdParts = column.id.split('-');
  const colIdSuffix = colIdParts[colIdParts.length - 1];

  return `${column.name} (C${colIdSuffix})`;
};

const flattenObj = (ob, prefix) => {
  const result = {};

  Object.keys(ob).forEach((i) => {
    if ((typeof ob[i]) === 'object' && !Array.isArray(ob[i])) {
      const temp = flattenObj(ob[i], '');
      Object.keys(temp).forEach((j) => {
        result[`${prefix}${i}.${j}`] = temp[j];
      });
    } else {
      result[i] = ob[i];
    }
  });

  return result;
};

const getContextVariables = (stream) => {
  const variables = Object.keys(flattenObj(stream.context, 'context.'));
  if (stream.context?.pricelist) {
    variables.push('context.pricelist_version.id');
    variables.push('context.pricelist_version.start_at');
  }

  if (stream.type === 'billing') {
    variables.push('context.period.start');
    variables.push('context.period.end');
  }

  return variables;
};

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

const getAddSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M19 13H13v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>';

const getDeleteSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M0 0h24v24H0V0z" fill="none"/><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12 1.41 1.41L13.41 14l2.12 2.12-1.41 1.41L12 15.41l-2.12 2.12-1.41-1.41L10.59 14l-2.13-2.12zM15.5 4l-1-1h-5l-1 1H5v2h14V4z"/></svg>';

const getAddButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('add-button');
  button.id = 'add-button';
  button.setAttribute('data-row-index', index);
  button.innerHTML = getAddSvg();

  return button;
};

const getDeleteButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('delete-button');
  button.id = `delete-${index}`;
  button.setAttribute('data-row-index', index);
  button.innerHTML = getDeleteSvg();

  return button;
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/lookup_subscription.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









const createOutputColumnForLookup = (prefix, name) => ({
  name: `${prefix}.${name}`,
  type: 'string',
  description: '',
});

const lookupSubscription = (app) => {
  if (!app) return;

  let columns = [];

  app.listen('config', async (config) => {
    const {
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = {
      external_id: 'CloudBlue Subscription External ID',
      id: 'CloudBlue Subscription ID',
      params__value: 'Parameter Value',
    };

    hideComponent('loader');
    showComponent('app');

    Object.keys(criteria).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = criteria[key];
      if (hasProduct === false && key === 'params__value') {
        option.disabled = true;
      }
      document.getElementById('criteria').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    if (hasProduct === true) {
      const parameters = await getLookupSubscriptionParameters(stream.context.product.id);
      parameters.forEach((element) => {
        const option = document.createElement('option');
        option.value = element.id;
        option.text = element.name;
        document.getElementById('parameter').appendChild(option);
      });
    }

    if (settings) {
      document.getElementById('criteria').value = settings.lookup_type;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      document.getElementById('prefix').value = settings.prefix;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('not_found_leave_empty').checked = true;
      } else {
        document.getElementById('not_found_fail').checked = true;
      }
      const multipleInput = document.getElementById(`multiple_${settings.action_if_multiple}`);
      if (multipleInput) {
        multipleInput.checked = true;
      } else {
        document.getElementById('multiple_fail').checked = true;
      }
      if (settings.lookup_type === 'params__value') {
        document.getElementById('parameter').value = settings.parameter.id;
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    } else {
      document.getElementById('param_name_group').style.display = 'none';
      document.getElementById('not_found_leave_empty').checked = true;
      document.getElementById('multiple_actual').checked = true;
    }

    document.getElementById('criteria').addEventListener('change', () => {
      if (document.getElementById('criteria').value === 'params__value') {
        document.getElementById('param_name_group').style.display = 'block';
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    });
  });

  app.listen('save', async () => {
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    const prefix = document.getElementById('prefix').value;
    let parameter = {};
    if (document.getElementById('criteria').value === 'params__value') {
      const select = document.getElementById('parameter');
      const paramName = select[select.selectedIndex].text;
      const paramID = select.value;
      parameter = { name: paramName, id: paramID };
    }
    const column = columns.find((c) => c.id === columnId);
    const actionIfNotFound = document.querySelector('input[name="if_not_found"]:checked').value;
    const actionIfMultiple = document.querySelector('input[name="if_multiple"]:checked').value;

    const data = {
      settings: {
        lookup_type: criteria,
        from: column.name,
        parameter,
        prefix,
        action_if_not_found: actionIfNotFound,
        action_if_multiple: actionIfMultiple,
      },
      columns: {
        input: [column],
        output: [
          'product.id',
          'product.name',
          'marketplace.id',
          'marketplace.name',
          'vendor.id',
          'vendor.name',
          'subscription.id',
          'subscription.external_id',
          'subscription.status',
        ].map((name) => createOutputColumnForLookup(prefix, name)),
      },
    };

    try {
      const overview = await validate('lookup_subscription', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(lookupSubscription);


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
/******/ 			228: 0
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
/******/ 		var chunkLoadingGlobal = self["webpackChunkconnect_transformations"] = self["webpackChunkconnect_transformations"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(262)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;