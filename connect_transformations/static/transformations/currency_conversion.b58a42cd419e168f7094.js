/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 491:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {


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

;// CONCATENATED MODULE: ./ui/src/pages/transformations/currency_conversion.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









const currencyConversionFormMainHTML = index => `
   <form name="convertCurrency-${index}" class="convert-currency">
  
      <div class="convert-currency__input-group">
          <div class="convert-currency__column convert-currency__input">
              <label for="input-column">Input Column</label>
              <select name="inputColumn" id="input-column-${index}"></select>
          </div>
  
          <div class="convert-currency__input">
              <label for="from-currency">From Currency</label>
              <select name="fromCurrency" id="from-currency-${index}"></select>
          </div>
      </div>
  
      <div class="convert-currency__input-group">
          <div class="convert-currency__column convert-currency__input">
              <label for="output-column">Output Column</label>
              <input name="outputColumn" id="output-column-${index}" type="text">
          </div>
  
          <div class="convert-currency__input">
              <label for="to-currency">To Currency</label>
              <select name="toCurrency" id="to-currency-${index}"></select>
          </div>
      </div>
  </form>
  
  <button id="delete-${index}" class="button form-delete-button">DELETE</button>
`;

const createCurrencyColumnOptions = (elem, currencies, selectedOption, disabledOption) => {
  elem.innerHTML = '';

  currencies.forEach(currency => {
    const option = document.createElement('option');
    const isSelected = selectedOption && currency.code === selectedOption;
    const isDisabled = disabledOption && currency.code === disabledOption;

    option.value = currency.code;
    option.text = `${currency.code} • ${currency.description}`;
    option.selected = isSelected;
    option.disabled = isDisabled;

    elem.appendChild(option);
  });
};

const createCurrencyConversionForm = (parent, index, columns, currencies, settings) => {
  const item = document.createElement('div');
  item.classList.add('form-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = currencyConversionFormMainHTML(index);

  parent.appendChild(item);

  const inputColumnSelect = document.getElementById(`input-column-${index}`);

  columns.forEach(column => {
    const isSelected = settings && settings.from.column === column.id;
    const colLabel = getColumnLabel(column);
    const option = isSelected ? `<option value="${column.id}" selected>${colLabel}</option>` : `<option value="${column.id}">${colLabel}</option>`;

    inputColumnSelect.innerHTML += option;
  });

  let selectedFromCurrency;
  let selectedToCurrency;

  if (settings) {
    const {
      from: { currency: inputCurrency },
      to: { column: outputCol, currency: outputCurrency },
    } = settings;

    const outputColumnInput = document.getElementById(`output-column-${index}`);

    outputColumnInput.value = outputCol;

    selectedFromCurrency = inputCurrency;
    selectedToCurrency = outputCurrency;
  } else {
    selectedFromCurrency = currencies[0].code;
    selectedToCurrency = currencies[1].code;
  }

  const fromCurrency = document.getElementById(`from-currency-${index}`);
  const toCurrency = document.getElementById(`to-currency-${index}`);

  createCurrencyColumnOptions(fromCurrency, currencies, selectedFromCurrency, selectedToCurrency);
  createCurrencyColumnOptions(toCurrency, currencies, selectedToCurrency, selectedFromCurrency);

  fromCurrency.addEventListener('change', () => {
    createCurrencyColumnOptions(toCurrency, currencies, toCurrency.value, fromCurrency.value);
  });

  toCurrency.addEventListener('change', () => {
    createCurrencyColumnOptions(fromCurrency, currencies, fromCurrency.value, toCurrency.value);
  });

  // handle delete button

  const buttons = document.getElementsByClassName('form-delete-button');

  for (let i = 0; i < buttons.length; i += 1) {
    if (buttons.length === 1) {
      buttons[i].disabled = true;
    } else {
      buttons[i].disabled = false;
    }
  }

  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    document.getElementById(`wrapper-${index}`).remove();

    if (buttons.length === 1) {
      buttons[0].disabled = true;
    }
  });
};


const convert = (app) => {
  if (!app) {
    return;
  }

  let formIndex = 0;
  let columns = [];
  let currencies = {};
  let settings;

  app.listen('config', async config => {
    settings = config.settings;
    columns = config.context.available_columns;
    currencies = await getCurrencies();

    const content = document.getElementById('content');

    if (!settings) {
      createCurrencyConversionForm(content, formIndex, columns, currencies);
    } else {
      if (!Array.isArray(settings)) {
        settings = [settings];
      }
      settings.forEach((setting, index) => {
        formIndex = index;
        createCurrencyConversionForm(content, formIndex, columns, currencies, setting);
      });
    }

    hideComponent('loader');
    showComponent('app');

    document.getElementById('add').addEventListener('click', () => {
      formIndex += 1;
      createCurrencyConversionForm(content, formIndex, columns, currencies);
    });
  });

  app.listen('save', async () => {
    const data = {
      settings: [],
      columns: {
        input: [],
        output: [],
      },
    };

    const filledForms = document.forms;

    // eslint-disable-next-line no-restricted-syntax
    for (const currentForm of filledForms) {
      const formElements = currentForm.elements;

      const inputColumnValue = formElements.inputColumn.value;
      const inputColumn = columns.find(column => column.id === inputColumnValue);

      const outputColumnValue = formElements.outputColumn.value;

      if (outputColumnValue === '' || outputColumnValue === null) {
        app.emit('validation-error', 'Output column name is required.');

        return;
      }

      const outputColumn = {
        name: outputColumnValue,
        type: 'decimal',
        description: '',
      };

      const currencyFromValue = formElements.fromCurrency.value;
      const currencyToValue = formElements.toCurrency.value;

      data.columns.input.push(inputColumn);
      data.columns.output.push(outputColumn);
      data.settings.push({
        from: {
          currency: currencyFromValue,
          column: inputColumnValue,
        },
        to: {
          currency: currencyToValue,
          column: outputColumn.name,
        },
      });
    }

    try {
      const overview = await validate('currency_conversion', data);

      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', {
        data: { ...data, ...overview },
        status: 'ok',
      });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(convert);


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
/******/ 			759: 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(491)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;