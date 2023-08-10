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
  getCurrencies, validate,
} from '../../utils';

import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


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
  });
};

createApp({ })
  .then(convert);
