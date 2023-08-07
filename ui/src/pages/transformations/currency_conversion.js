/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import {
  getColumnLabel,
  getCurrencies,
} from '../../utils';

import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


export const createCurrencyColumnOptions = (elem, currencies, selectedOption, disabledOption) => {
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

export const createCurrencyConversionForm = (parent, index, columns, currencies) => {
  const item = document.createElement('div');
  item.classList.add('form-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
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
      
      <button id="delete-${index}" class="button">DELETE</button>
    `;
  parent.appendChild(item);

  // add input column options

  const inputColumnSelect = document.getElementById(`input-column-${index}`);

  columns.forEach(column => {
    const colLabel = getColumnLabel(column);
    const option = `<option value="${column.id}">${colLabel}</option>`;

    inputColumnSelect.innerHTML += option;
  });

  // add currencies options

  let selectedToCurrency;
  let selectedFromCurrency;

  // eslint-disable-next-line prefer-const
  [selectedFromCurrency] = [currencies[0].code];
  // eslint-disable-next-line prefer-const
  [selectedToCurrency] = [currencies[1].code];


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


const convert = (app) => {
  if (!app) {
    return;
  }

  let formIndex = 0;
  let columns = [];
  let currencies = {};

  app.listen('config', async config => {
    const {
      context: { available_columns: availableColumns },
    } = config;

    columns = availableColumns;
    currencies = await getCurrencies();

    const content = document.getElementById('content');

    createCurrencyConversionForm(content, formIndex, columns, currencies);

    hideComponent('loader');
    showComponent('app');

    document.getElementById('add').addEventListener('click', () => {
      formIndex += 1;
      createCurrencyConversionForm(content, formIndex, columns, currencies);
    });
  });

  app.listen('save', () => {
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
    }
  });
};

createApp({ })
  .then(convert);
