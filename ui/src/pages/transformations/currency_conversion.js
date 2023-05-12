/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import {
  getCurrencies,
  validate,
} from '../../utils';

import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


const convert = (app) => {
  if (!app) {
    return;
  }

  let columns = [];
  let currencies = {};

  const createCurrencyColumnOptions = (elemId, selectedOption, disabledOption) => {
    const selectCurrencyColumnSelect = document.getElementById(elemId);
    selectCurrencyColumnSelect.innerHTML = '';

    currencies.forEach(currency => {
      const isSelected = selectedOption && currency.code === selectedOption;
      const isDisabled = disabledOption && currency.code === disabledOption;

      const option = document.createElement('option');
      option.value = currency.code;
      option.text = `${currency.code} • ${currency.description}`;
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
      [selectedFromCurrency] = [currencies[0].code];
      [selectedToCurrency] = [currencies[1].code];
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
      showError('This fields may not be equal: columns.input.name, columns.output.name.');
    } else if (outputColumnValue === '' || outputColumnValue === null) {
      showError('Output column name is required.');
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
        showError(e);
      }
    }
  });
};

createApp({ })
  .then(convert);
