/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 608:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {


// UNUSED EXPORTS: createManualOutputRow, manual

// EXTERNAL MODULE: ./node_modules/@cloudblueconnect/connect-ui-toolkit/dist/index.js
var dist = __webpack_require__(164);
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


const buildOutputColumnInput = ({
  parent,
  column,
  index,
  additionalInputs,
  showName = true,
  showType = true,
  showDelete = true,
}) => {
  const container = document.createElement('div');
  container.id = index;
  container.classList.add('output-column-container');

  parent.appendChild(container);

  if (showName) {
    const nameInput = document.createElement('input');
    nameInput.classList.add('output-column-name');
    nameInput.type = 'text';
    nameInput.id = `name-${container.id}`;
    nameInput.placeholder = 'Column name';
    nameInput.value = column?.name || '';
    container.appendChild(nameInput);
  }

  if (showType) {
    const typeSelect = document.createElement('select');
    typeSelect.classList.add('output-column-type');
    typeSelect.style.flexGrow = '1';
    typeSelect.id = `type-${container.id}`;
    typeSelect.innerHTML = `
      <option value="string" selected>String</option>
      <option value="integer">Integer</option>
      <option value="decimal">Decimal</option>
      <option value="boolean">Boolean</option>
      <option value="datetime">Datetime</option>
    `;
    typeSelect.value = column?.type || 'string';
    container.appendChild(typeSelect);

    const precisionSelect = document.createElement('select');
    precisionSelect.classList.add('output-column-precision');
    precisionSelect.id = `precision-${container.id}`;
    typeSelect.style.flexShrink = '100';
    precisionSelect.innerHTML = `
      <option value="auto" selected>Auto</option>
      <option value="1">1 decimal</option>
      <option value="2">2 decimals</option>
      <option value="3">3 decimals</option>
      <option value="4">4 decimals</option>
      <option value="5">5 decimals</option>
      <option value="6">6 decimals</option>
      <option value="7">7 decimals</option>
      <option value="8">8 decimals</option>
    `;

    if (column?.type === 'decimal') {
      precisionSelect.style.display = 'block';
      precisionSelect.value = column.constraints?.precision || 'auto';
    } else {
      precisionSelect.style.display = 'none';
      precisionSelect.value = null;
    }

    container.appendChild(precisionSelect);

    typeSelect.addEventListener('change', () => {
      if (typeSelect.value === 'decimal') {
        precisionSelect.style.display = 'block';
        precisionSelect.value = 'auto';
      } else {
        precisionSelect.style.display = 'none';
        precisionSelect.value = null;
      }
    });
  }

  additionalInputs?.forEach(customInput => container.appendChild(customInput));

  if (showDelete) {
    const deleteButton = document.createElement('button');
    deleteButton.id = `delete-${container.id}`;
    deleteButton.classList.add('button', 'delete-button', 'output-column-delete');
    deleteButton.innerHTML = 'DELETE';
    container.appendChild(deleteButton);

    deleteButton?.addEventListener('click', () => {
      parent.remove();
      const buttons = document.getElementsByClassName('delete-button');
      if (buttons.length === 1) {
        buttons[0].disabled = true;
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
  }
};

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

const getLookupSubscriptionParameters = (productId, tfn = 'subscription') => fetch(`/api/lookup_${tfn}/parameters?product_id=${productId}`, {
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


const getDataFromOutputColumnInput = (index) => {
  const data = {};

  const nameInput = document.getElementById(`name-${index}`);
  if (nameInput) {
    data.name = nameInput.value;
  }

  const typeInput = document.getElementById(`type-${index}`);
  if (typeInput) {
    data.type = typeInput.value;
  }

  const precisionInput = document.getElementById(`precision-${index}`);
  if (
    data.type === 'decimal'
    && precisionInput
    && precisionInput.value !== 'auto'
  ) {
    data.constraints = { precision: precisionInput.value };
  }

  return data;
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/manual.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









const createManualOutputRow = (parent, index, column) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  parent.appendChild(item);
  buildOutputColumnInput({
    column,
    index,
    parent: item,
  });
};

const manual = (app) => {
  if (!app) {
    return;
  }

  hideComponent('app');
  hideComponent('loader');

  let availableColumns;
  let rowIndex = 0;

  const descriptionElement = document.getElementById('description-text');
  const settingsElement = document.getElementById('settings-text');

  app.listen('config', (config) => {
    const {
      columns: { input: inputColumns, output: outputColumns },
      context: { available_columns }, // eslint-disable-line camelcase
      overview,
      settings,
    } = config;

    availableColumns = available_columns; // eslint-disable-line camelcase

    descriptionElement.value = overview || '';
    settingsElement.value = settings ? JSON.stringify(settings) : '{}';

    const inputColumnsEditElement = document.getElementById('edit-input-columns');
    availableColumns.forEach((column) => {
      const checked = inputColumns.some((inputColumn) => inputColumn.id === column.id);
      const inputColumnRow = document.createElement('tr');
      inputColumnRow.innerHTML = `
        <td>${column.id.slice(-3)}</td>
        <td>${column.name}</td>
        <td>${column.type}</td>
        <td>${column.description ? column.description : '-'}</td>
        <td><input id="${column.id}" type="checkbox" ${checked ? 'checked' : ''} /></td>
      `;
      inputColumnsEditElement.appendChild(inputColumnRow);
    });

    const outputColumnsElement = document.getElementById('output-columns');

    if (outputColumns.length > 0) {
      outputColumns.forEach((outputColumn, index) => {
        rowIndex = index;
        createManualOutputRow(outputColumnsElement, rowIndex, outputColumn);
      });
    } else {
      createManualOutputRow(outputColumnsElement, rowIndex);
    }

    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createManualOutputRow(outputColumnsElement, rowIndex);
    });

    descriptionElement.addEventListener('keyup', () => {
      const maxLength = 2000;
      const currentLength = descriptionElement.value.length;
      const descriptionLabel = document.getElementById('description-label');
      const errorHint = document.getElementById('description-text-hint');
      const descriptionCounter = document.getElementById('description-text-counter');

      descriptionCounter.innerHTML = `${currentLength} / ${maxLength}`;
      app.emit('overview-changed', descriptionElement.value);

      if (currentLength > Number(maxLength)) {
        descriptionLabel.classList.add('error--text');
        descriptionCounter.classList.add('error--text');
        descriptionElement.classList.add('error--input');
        errorHint.classList.remove('text-hidden');
      } else {
        descriptionLabel.classList.remove('error--text');
        descriptionCounter.classList.remove('error--text');
        descriptionElement.classList.remove('error--input');
        errorHint.classList.add('text-hidden');
      }
    });

    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', () => {
    const data = {
      settings: {},
      columns: {
        input: [],
        output: [],
      },
      overview: '',
    };

    try {
      data.overview = descriptionElement.value;
      data.settings = JSON.parse(settingsElement.value);
      const inputColumns = document.querySelectorAll('#edit-input-columns-table input[type="checkbox"]:checked');
      inputColumns.forEach((inputColumn) => {
        const availableColumn = availableColumns.find((column) => column.id === inputColumn.id);
        data.columns.input.push(availableColumn);
      });

      const outputs = document.getElementsByClassName('output-column-container');
      for (let i = 0; i < outputs.length; i += 1) {
        const index = outputs[i].id;
        data.columns.output.push(getDataFromOutputColumnInput(index));
      }

      app.emit('save', {
        data,
        status: 'ok',
      });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(manual);


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
/******/ 			577: 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(608)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;