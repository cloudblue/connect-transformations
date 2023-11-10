/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 84:
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

;// CONCATENATED MODULE: ./ui/src/pages/transformations/lookup_billing_request.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/









const AVAILABLE_BILLING_REQUEST_ATTRS = [
  {
    value: 'id',
    label: 'Billing Request ID',
  },
  {
    value: 'events.created.at',
    label: 'Billing Request created at',
  },
  {
    value: 'events.updated.at',
    label: 'Billing Request updated at',
  },
  {
    value: 'asset.id',
    label: 'Subscription ID',
  },
  {
    value: 'asset.status',
    label: 'Subscription status',
  },
  {
    value: 'asset.external_id',
    label: 'Subscription external id',
  },
  {
    value: 'asset.external_uid',
    label: 'Subscription UID',
  },
  {
    value: 'asset.product.id',
    label: 'Product id',
  },
  {
    value: 'asset.product.name',
    label: 'Product name',
  },
  {
    value: 'asset.product.status',
    label: 'Product status',
  },
  {
    value: 'asset.connection.provider.id',
    label: 'Distributor ID',
  },
  {
    value: 'asset.connection.provider.name',
    label: 'Distributor name',
  },
  {
    value: 'asset.connection.vendor.id',
    label: 'Vendor ID',
  },
  {
    value: 'asset.connection.vendor.name',
    label: 'Vendor name',
  },
  {
    value: 'asset.connection.hub.id',
    label: 'Hub id',
  },
  {
    value: 'asset.connection.hub.name',
    label: 'Hub name',
  },
  {
    value: 'asset.tiers.customer.id',
    label: 'Customer ID',
  },
  {
    value: 'asset.tiers.customer.external_id',
    label: 'Customer external ID',
  },
  {
    value: 'asset.tiers.customer.external_uid',
    label: 'Customer external UID',
  },
  {
    value: 'asset.tiers.customer.name',
    label: 'Customer name',
  },
  {
    value: 'asset.tiers.tier1.id',
    label: 'Tier1 ID',
  },
  {
    value: 'asset.tiers.tier1.external_id',
    label: 'Tier1 external ID',
  },
  {
    value: 'asset.tiers.tier1.external_uid',
    label: 'Tier1 external UID',
  },
  {
    value: 'asset.tiers.tier1.name',
    label: 'Tier1 name',
  },
  {
    value: 'asset.tiers.tier2.id',
    label: 'Tier2 ID',
  },
  {
    value: 'asset.tiers.tier2.external_id',
    label: 'Tier2 external ID',
  },
  {
    value: 'asset.tiers.tier2.external_uid',
    label: 'Tier2 external UID',
  },
  {
    value: 'asset.tiers.tier2.name',
    label: 'Tier2 name',
  },
  {
    value: 'asset.marketplace.id',
    label: 'Marketplace ID',
  },
  {
    value: 'asset.marketplace.name',
    label: 'Marketplace name',
  },
  {
    value: 'asset.contract.id',
    label: 'Contract ID',
  },
  {
    value: 'asset.contract.name',
    label: 'Contract name',
  },
  {
    value: 'asset.parameter.value',
    label: 'Parameter value',
  },
  {
    value: 'items.id',
    label: 'Product item IDs',
  },
  {
    value: 'items.global_id',
    label: 'Product item global IDs',
  },
  {
    value: 'items.mpn',
    label: 'Product item MPNs',
  },
  {
    value: 'items.item_type',
    label: 'Product item types',
  },
  {
    value: 'items.quantity',
    label: 'Product item quantity',
  },
  {
    value: 'items.old_quantity',
    label: 'Product item previous quantity',
  },
  {
    value: 'items.period',
    label: 'Product item period',
  },
];


const createOutputRow = (parent, index, column, parameters, columnConfigs) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  parent.appendChild(item);

  const columnConfig = columnConfigs?.[column.name];

  const sourceSelect = document.createElement('select');
  sourceSelect.id = `source-select-${index}`;
  sourceSelect.classList.add('output-column-source');

  AVAILABLE_BILLING_REQUEST_ATTRS.forEach(optionData => {
    const option = document.createElement('option');
    option.value = optionData.value;
    option.innerHTML = optionData.label;

    sourceSelect.appendChild(option);
  });
  if (columnConfig) {
    sourceSelect.value = columnConfig.attribute;
  }

  const paramNameSelect = document.createElement('select');
  paramNameSelect.id = `source-param-select-${index}`;

  parameters.forEach(param => {
    const paramOption = document.createElement('option');
    paramOption.value = param.name;
    paramOption.text = param.name;
    paramNameSelect.appendChild(paramOption);
  });
  if (columnConfig?.parameter_name) {
    paramNameSelect.value = columnConfig.parameter_name;
  }

  buildOutputColumnInput({
    column,
    index,
    parent: item,
    additionalInputs: [sourceSelect, paramNameSelect],
    showType: false,
  });

  const handleSourceSelectChange = () => {
    if (sourceSelect.value === 'asset.parameter.value') {
      paramNameSelect.style.display = 'block';
      paramNameSelect.style.maxWidth = 'calc(28% - 10px)';
      sourceSelect.style.maxWidth = 'calc(25% - 10px)';
    } else {
      paramNameSelect.style.display = 'none';
      sourceSelect.style.maxWidth = null;
    }
  };

  handleSourceSelectChange();
  sourceSelect.addEventListener('change', handleSourceSelectChange);
};

const lookupBillingRequest = (app) => {
  if (!app) return;

  let columns = [];
  let parameters = [];

  app.listen('config', async (config) => {
    const {
      columns: { output: outputColumns },
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;
    const outputConfigs = settings?.output_config;
    let rowIndex = 0;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = {
      external_id: 'CloudBlue Subscription External ID',
      id: 'CloudBlue Subscription ID',
      skip: 'Skip search by Subscription',
    };

    const item = {
      id: 'Item ID',
      global_id: 'Item Global ID',
      mpn: 'Item MPN',
      all: 'Include all',
    };

    hideComponent('loader');
    showComponent('app');

    Object.keys(criteria).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = criteria[key];
      document.getElementById('criteria').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    Object.keys(item).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = item[key];
      document.getElementById('item').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('item_column').appendChild(option);
    });

    if (hasProduct === true) {
      parameters = await getLookupSubscriptionParameters(stream.context.product.id, 'billing_request');
      parameters.forEach((element) => {
        const option = document.createElement('option');
        option.value = element.id;
        option.text = element.name;
        document.getElementById('parameter').appendChild(option);
      });

      availableColumns.forEach((column) => {
        const option = document.createElement('option');
        option.value = column.id;
        option.text = getColumnLabel(column);
        document.getElementById('parameter_column').appendChild(option);
      });
    }

    if (settings) {
      if (settings.asset_type === null) {
        document.getElementById('criteria').value = 'skip';
        document.getElementById('subscription_column').style.display = 'none';
      } else {
        const columnId = columns.find((c) => c.name === settings.asset_column).id;
        document.getElementById('criteria').value = settings.asset_type || 'skip';
        document.getElementById('column').value = columnId;
      }

      document.getElementById('parameter').value = settings.parameter.id;
      const parameterColId = columns.find((c) => c.name === settings.parameter_column).id;
      document.getElementById('parameter_column').value = parameterColId;

      document.getElementById('item').value = settings.item.id;
      if (['skip', 'all'].includes(settings.item.id)) {
        document.getElementById('item_column_group').style.display = 'none';
      } else {
        const itemId = columns.find((c) => c.name === settings.item_column).id;
        document.getElementById('item_column').value = itemId;
      }

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
    } else {
      document.getElementById('not_found_leave_empty').checked = true;
      document.getElementById('multiple_use_most_actual').checked = true;
    }

    document.getElementById('criteria').addEventListener('change', () => {
      if (document.getElementById('criteria').value === 'skip') {
        document.getElementById('subscription_column').style.display = 'none';
      } else {
        document.getElementById('subscription_column').style.display = 'block';
      }
    });

    document.getElementById('item').addEventListener('change', () => {
      if (document.getElementById('item').value === 'all') {
        document.getElementById('item_column_group').style.display = 'none';
      } else {
        document.getElementById('item_column_group').style.display = 'block';
      }
    });

    const outputColumnsElement = document.getElementById('output-columns');

    if (outputColumns.length > 0) {
      outputColumns.forEach((outputColumn, index) => {
        rowIndex = index;
        createOutputRow(outputColumnsElement, rowIndex, outputColumn, parameters, outputConfigs);
      });
    } else {
      createOutputRow(outputColumnsElement, rowIndex, undefined, parameters);
    }
    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createOutputRow(outputColumnsElement, rowIndex, undefined, parameters);
    });
  });

  app.listen('save', async () => {
    let assetType = document.getElementById('criteria').value;
    let assetColumn = null;
    if (assetType === 'skip') {
      assetType = null;
    } else {
      assetColumn = columns.find((c) => c.id === document.getElementById('column').value);
    }

    let select = document.getElementById('parameter');
    const parameter = { name: select[select.selectedIndex].text, id: select.value };
    const parameterColumn = columns.find((c) => c.id === document.getElementById('parameter_column').value);

    select = document.getElementById('item');
    const item = { name: select[select.selectedIndex].text, id: select.value };
    const itemColumn = columns.find((c) => c.id === document.getElementById('item_column').value);


    const actionIfNotFound = document.querySelector('input[name="if_not_found"]:checked').value;
    const actionIfMultiple = document.querySelector('input[name="if_multiple"]:checked').value;

    const outputs = document.getElementsByClassName('output-column-container');
    const outputColumnsData = [];
    const outputColumnsConfig = {};

    for (let i = 0; i < outputs.length; i += 1) {
      const index = outputs[i].id;
      const sourceSelect = document.getElementById(`source-select-${index}`);
      const colSource = sourceSelect.value;
      let colName = getDataFromOutputColumnInput(index).name;
      const columnConfig = {
        attribute: colSource,
      };

      if (colSource === 'asset.parameter.value') {
        const paramName = document.getElementById(`source-param-select-${index}`).value;
        columnConfig.parameter_name = paramName;
      }

      if (!colName) {
        colName = sourceSelect.options[sourceSelect.selectedIndex].label;
        if (columnConfig.parameter_name) {
          colName += ` ${columnConfig.parameter_name}`;
        }
      }

      outputColumnsData.push({
        name: colName,
        type: 'string',
      });
      outputColumnsConfig[colName] = columnConfig;
    }

    const settings = {
      parameter,
      parameter_column: parameterColumn.name,
      asset_type: assetType,
      asset_column: assetColumn == null ? null : assetColumn.name,
      item,
      item_column: itemColumn.name,
      action_if_not_found: actionIfNotFound,
      action_if_multiple: actionIfMultiple,
      output_config: outputColumnsConfig,
    };
    let inputColumns = [];
    if (assetColumn != null) {
      inputColumns = [assetColumn, itemColumn, parameterColumn];
    } else {
      inputColumns = [itemColumn, parameterColumn];
    }

    const data = {
      settings,
      columns: {
        input: inputColumns,
        output: outputColumnsData,
      },
    };

    try {
      const overview = await validate('lookup_billing_request', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(lookupBillingRequest);


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
/******/ 			435: 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(84)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;