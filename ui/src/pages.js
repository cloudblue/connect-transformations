/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import {
  getCurrencies,
  getLookupSubscriptionCriteria,
  validate,
} from './utils';

import {
  hideComponent,
  showComponent,
} from './components';


export const createCopyRow = (parent, index, options, input, output) => {
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

export const copy = (app) => {
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

export const lookupSubscription = (app) => {
  if (!app) return;

  let columns = [];

  app.listen('config', async (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;
    const criteria = await getLookupSubscriptionCriteria();

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
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('criteria').value = settings.lookup_type;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      document.getElementById('prefix').value = settings.prefix;
    }
  });

  app.listen('save', async () => {
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    const prefix = document.getElementById('prefix').value;
    const column = columns.find((c) => c.id === columnId);

    const data = {
      settings: {
        lookup_type: criteria,
        from: column.name,
        prefix,
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

export const convert = (app) => {
  if (!app) {
    return;
  }

  let columns = [];
  let currencies = {};

  const createCurrencyColumnOptions = (elemId, selectedOption) => {
    const fromCurrencyColumnSelect = document.getElementById(elemId);

    Object.keys(currencies).forEach(currency => {
      const currencyFullName = currencies[currency];
      const isSelected = selectedOption && currency === selectedOption;

      const option = isSelected ? `<option value="${currency}" selected>${currency} • ${currencyFullName}</option>` : `<option value="${currency}">${currency} • ${currencyFullName}</option>`;

      fromCurrencyColumnSelect.innerHTML += option;
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

    if (settings) {
      outputColumnInput.value = settings.to.column;

      selectedFromCurrency = settings.from.currency;
      selectedToCurrency = settings.to.currency;
    }

    currencies = await getCurrencies();

    createCurrencyColumnOptions('from-currency', selectedFromCurrency);
    createCurrencyColumnOptions('to-currency', selectedToCurrency);

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
        type: inputColumn.type,
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
