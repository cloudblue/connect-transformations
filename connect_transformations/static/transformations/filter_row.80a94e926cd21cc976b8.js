/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 986:
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
const utils_validate = (functionName, data) => fetch(`/api/validate/${functionName}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

const utils_getLookupSubscriptionCriteria = () => fetch('/api/lookup_subscription/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const utils_getLookupSubscriptionParameters = (productId) => fetch(`/api/lookup_subscription/parameters?product_id=${productId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const utils_getCurrencies = () => fetch('/api/currency_conversion/currencies').then(response => response.json());

/* The data should contain pattern (and optionally groups) keys.
We expect the return groups key (with the new keys found in the regex) and the order
 (to display in order on the UI) */
const utils_getGroups = (data) => fetch('/api/split_column/extract_groups', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());


/* The data should contain list of jq expressions and all input columns.
We expect to return columns used in expressions */
const utils_getJQInput = (data) => fetch('/api/formula/extract_input', {
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
const components_showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

const components_hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};

;// CONCATENATED MODULE: ./ui/src/pages.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/





const createCopyRow = (parent, index, options, input, output) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <select class="list" style="width: 35%;" ${input ? `value="${input.id}"` : ''}>
        ${options.map((column) => `
          <option value="${column.id}" ${input && input.id === column.id ? 'selected' : ''}>
            ${column.name}
          </option>`).join(' ')}
      </select>
      <input type="text" placeholder="Copy column name" style="width: 35%;" ${output ? `value="${output.name}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
    `;
  parent.appendChild(item);
  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      window.alert('You need to have at least one row');
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

const createManualOutputRow = (parent, index, output) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '450px';
  item.innerHTML = `
      <input type="text" class="output-column-name" placeholder="Output column name" style="width: 75%;" ${output ? `value="${output.name}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
    `;
  parent.appendChild(item);
  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      window.alert('You need to have at least one row');
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

const copy = (app) => {
  if (!app) return;

  hideComponent('loader');
  showComponent('app');

  let rowIndex = 0;
  let columns = [];

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      columns: { input: inputColumns, output: outputColumns },
      settings,
    } = config;

    columns = availableColumns;

    const content = document.getElementById('content');
    if (!settings) {
      createCopyRow(content, rowIndex, columns);
    } else {
      settings.forEach((setting, i) => {
        const inputColumn = inputColumns.find((column) => column.name === setting.from);
        const outputColumn = outputColumns.find((column) => column.name === setting.to);
        rowIndex = i;
        createCopyRow(content, rowIndex, columns, inputColumn, outputColumn);
      });
    }
    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createCopyRow(content, rowIndex, columns);
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
    const form = document.getElementsByClassName('list-wrapper');
    // eslint-disable-next-line no-restricted-syntax
    for (const line of form) {
      const inputId = line.getElementsByTagName('select')[0].value;
      const outputName = line.getElementsByTagName('input')[0].value;

      const inputColumn = columns.find((column) => column.id === inputId);
      const outputColumn = {
        name: outputName,
        type: inputColumn.type,
        description: '',
      };
      const setting = {
        from: inputColumn.name,
        to: outputName,
      };
      data.settings.push(setting);
      data.columns.input.push(inputColumn);
      data.columns.output.push(outputColumn);
    }

    try {
      const overview = await validate('copy_columns', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      window.alert(e);
    }
  });
};

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
    const criteria = await getLookupSubscriptionCriteria();

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
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (hasProduct === true) {
      const parameters = await getLookupSubscriptionParameters(stream.context.product.id);
      Object.values(parameters).forEach((element) => {
        Object.keys(element).forEach((key) => {
          const option = document.createElement('option');
          option.value = key;
          option.text = element[key];
          document.getElementById('parameter').appendChild(option);
        });
      });
    }

    if (settings) {
      document.getElementById('criteria').value = settings.lookup_type;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      document.getElementById('prefix').value = settings.prefix;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('leave_empty').checked = true;
      } else {
        document.getElementById('fail').checked = true;
      }
      if (settings.lookup_type === 'params__value') {
        document.getElementById('parameter').value = settings.parameter.id;
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    } else {
      document.getElementById('param_name_group').style.display = 'none';
      document.getElementById('leave_empty').checked = true;
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
    const actionIfNotFound = document.getElementById('leave_empty').checked ? 'leave_empty' : 'fail';

    const data = {
      settings: {
        lookup_type: criteria,
        from: column.name,
        parameter,
        prefix,
        action_if_not_found: actionIfNotFound,
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
      window.alert(e);
    }
  });
};

const convert = (app) => {
  if (!app) {
    return;
  }

  let columns = [];
  let currencies = {};

  const createCurrencyColumnOptions = (elemId, selectedOption, disabledOption) => {
    const selectCurrencyColumnSelect = document.getElementById(elemId);
    selectCurrencyColumnSelect.innerHTML = '';

    Object.keys(currencies).forEach(currency => {
      const currencyFullName = currencies[currency];
      const isSelected = selectedOption && currency === selectedOption;
      const isDisabled = disabledOption && currency === disabledOption;

      const option = document.createElement('option');
      option.value = currency;
      option.text = `${currency} • ${currencyFullName}`;
      option.selected = isSelected;
      option.disabled = isDisabled;
      selectCurrencyColumnSelect.appendChild(option);
    });
  };

  app.listen('config', async config => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;

    const inputColumnSelect = document.getElementById('input-column');
    const outputColumnInput = document.getElementById('output-column');

    columns.forEach(column => {
      const isSelected = settings && column.name === settings.from.column;

      const option = isSelected ? `<option value="${column.id}" selected>${column.name}</option>` : `<option value="${column.id}">${column.name}</option>`;

      inputColumnSelect.innerHTML += option;
    });

    let selectedToCurrency;
    let selectedFromCurrency;

    currencies = await getCurrencies();

    if (settings) {
      outputColumnInput.value = settings.to.column;

      selectedFromCurrency = settings.from.currency;
      selectedToCurrency = settings.to.currency;
    } else {
      [selectedFromCurrency] = Object.keys(currencies).slice(0, 1);
      [selectedToCurrency] = Object.keys(currencies).slice(1, 2);
    }

    createCurrencyColumnOptions('from-currency', selectedFromCurrency, selectedToCurrency);
    createCurrencyColumnOptions('to-currency', selectedToCurrency, selectedFromCurrency);

    hideComponent('loader');
    showComponent('app');

    const fromCurrency = document.getElementById('from-currency');
    const toCurrency = document.getElementById('to-currency');

    fromCurrency.addEventListener('change', () => {
      createCurrencyColumnOptions('to-currency', toCurrency.value, fromCurrency.value);
    });

    toCurrency.addEventListener('change', () => {
      createCurrencyColumnOptions('from-currency', fromCurrency.value, toCurrency.value);
    });
  });

  app.listen('save', async () => {
    const data = {
      settings: {},
      columns: {
        input: [],
        output: [],
      },
    };

    const formElements = document.forms.convertCurrency.elements;

    const inputColumnValue = formElements.inputColumn.value;
    const inputColumn = columns.find(column => column.id === inputColumnValue);

    const outputColumnValue = formElements.outputColumn.value;

    if (outputColumnValue === inputColumn.name) {
      window.alert('This fields may not be equal: columns.input.name, columns.output.name.');
    } else {
      const outputColumn = {
        name: outputColumnValue,
        type: 'decimal',
        description: '',
      };

      const currencyFromValue = formElements.fromCurrency.value;
      const currencyToValue = formElements.toCurrency.value;

      data.columns.input.push(inputColumn);
      data.columns.output.push(outputColumn);
      data.settings = {
        from: {
          currency: currencyFromValue,
          column: inputColumn.name,
        },
        to: {
          currency: currencyToValue,
          column: outputColumn.name,
        },
      };

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
        window.alert(e);
      }
    }
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

      const outputColumnsElements = document.getElementsByClassName('output-column-name');
      // eslint-disable-next-line no-restricted-syntax
      for (const outputColumnElement of outputColumnsElements) {
        const outputColumn = {
          name: outputColumnElement.value,
          type: 'string',
          description: '',
        };
        data.columns.output.push(outputColumn);
      }

      app.emit('save', {
        data,
        status: 'ok',
      });
    } catch (e) {
      window.alert(e);
    }
  });
};

function getCurrentGroups(parent) {
  const descendents = parent.getElementsByTagName('input');
  const currentGroups = {};
  for (let i = 0; i < descendents.length; i += 1) {
    const element = descendents[i];
    currentGroups[element.id] = element.value;
  }

  return currentGroups;
}

function buildGroups(groups) {
  const parent = document.getElementById('output');
  parent.innerHTML = '';
  Object.keys(groups).forEach(groupKey => {
    const groupValue = groups[groupKey];
    const item = document.createElement('div');
    item.style.width = '200px';
    item.innerHTML = `
    <input
    type="text" class="output-input" id="${groupKey}"
    placeholder="${groupKey} value"
    style="width: 100%;" value="${groupValue}"/>
    `;
    parent.appendChild(item);
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
      window.alert(response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    window.alert('The regular expression is empty');
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
      data.columns.output.push({
        name: option.value,
        type: inputColumn.type,
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
      window.alert(e);
      showComponent('app');
      hideComponent('loader');
    }
  });
};

const createFormulaRow = (parent, index, output, formula) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <input type="text" placeholder="Output column" style="width: 70%;" ${output ? `value="${output}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
      <div class="input-group">
          <label class="label" for="formula-${index}">Formula:</label>
          <textarea id="formula-${index}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
      </div>
    `;
  parent.appendChild(item);
  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      window.alert('You need to have at least one row');
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

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;

    const content = document.getElementById('content');
    if (settings && settings.expressions) {
      settings.expressions.forEach((expression, i) => {
        rowIndex = i;
        createFormulaRow(content, rowIndex, expression.to, expression.formula);
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

      const outputColumn = {
        name: to,
        description: '',
        type: 'string',
        nullable: true,
      };
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
      window.alert(e);
    }
  });
};


const filterRow = (app) => {
  if (!app) return;

  let columns = [];

  components_hideComponent('loader');
  components_showComponent('app');

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    components_showComponent('loader');
    components_hideComponent('app');

    columns = availableColumns;

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('value').value = settings.value;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
    }
    components_hideComponent('loader');
    components_showComponent('app');
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

    components_showComponent('loader');
    components_hideComponent('app');

    const inputSelector = document.getElementById('column');
    const selectedColumn = inputSelector.options[inputSelector.selectedIndex].text;
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    data.columns.input.push(inputColumn);
    data.columns.output.push(
      {
        name: `${selectedColumn}_INSTRUCTIONS`,
        type: 'string',
        output: false,
      },
    );

    const inputValue = document.getElementById('value');
    data.settings = {
      from: selectedColumn,
      value: inputValue.value,
    };

    try {
      const overview = await utils_validate('filter_row', data);
      if (overview.error) {
        throw new Error(overview.error);
      }

      if (data.columns.output.length === 0) {
        throw new Error('No output columns defined');
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      window.alert(e);
      components_showComponent('app');
      components_hideComponent('loader');
    }
  });
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/filter_row.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/







(0,dist/* default */.ZP)({ })
  .then(filterRow);


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
/******/ 			429: 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(986)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;