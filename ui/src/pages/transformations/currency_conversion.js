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
  validate,
} from '../../utils';

import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


export const createCurrencyColumnOptions = (elem, currencies) => {
  elem.innerHTML = '';

  currencies.forEach(currency => {
    const option = document.createElement('option');
    option.value = currency.code;
    option.text = `${currency.code} • ${currency.description}`;

    elem.appendChild(option);
  });
};

export const createCurrencyConversionColumn = (parent, index, columns, currencies) => {
  // eslint-disable-next-line no-console
  console.log(currencies);
  const item = document.createElement('div');
  item.classList.add('form-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
        <form name="convertCurrency" class="convert-currency">

          <div class="convert-currency__input-group">
              <div class="convert-currency__column convert-currency__input">
                  <label for="input-column">Input Column</label>
                  <select name="inputColumn" id="input-column"></select>
              </div>

              <div class="convert-currency__input">
                  <label for="from-currency">From Currency</label>
                  <select name="fromCurrency" id="from-currency"></select>
              </div>
          </div>

          <div class="convert-currency__input-group">
              <div class="convert-currency__column convert-currency__input">
                  <label for="output-column">Output Column</label>
                  <input name="outputColumn" id="output-column" type="text">
              </div>

              <div class="convert-currency__input">
                  <label for="to-currency">To Currency</label>
                  <select name="toCurrency" id="to-currency"></select>
              </div>
          </div>
      </form>
      
      <button id="delete-${index}" class="button">DELETE</button>
    `;
  parent.appendChild(item);

  // add input column options

  const inputColumnSelect = document.getElementById('input-column');

  columns.forEach(column => {
    const colLabel = getColumnLabel(column);
    const option = `<option value="${column.id}">${colLabel}</option>`;

    inputColumnSelect.innerHTML += option;
  });

  // add currencies options

  const fromCurrency = document.getElementById('from-currency');
  const toCurrency = document.getElementById('to-currency');

  createCurrencyColumnOptions(fromCurrency, currencies);
  createCurrencyColumnOptions(toCurrency, currencies);

  fromCurrency.addEventListener('change', () => {
    createCurrencyColumnOptions('to-currency', toCurrency.value, fromCurrency.value);
  });

  toCurrency.addEventListener('change', () => {
    createCurrencyColumnOptions('from-currency', fromCurrency.value, toCurrency.value);
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

    createCurrencyConversionColumn(content, formIndex, columns, currencies);

    hideComponent('loader');
    showComponent('app');

    document.getElementById('add').addEventListener('click', () => {
      formIndex += 1;
      createCurrencyConversionColumn(content, formIndex, columns, currencies);
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


// const convert = (app) => {
//   if (!app) {
//     return;
//   }
//
//   let columns = [];
//   let currencies = {};
//
//   const createCurrencyColumnOptions = (elemId, selectedOption, disabledOption) => {
//     const selectCurrencyColumnSelect = document.getElementById(elemId);
//     selectCurrencyColumnSelect.innerHTML = '';
//
//     currencies.forEach(currency => {
//       const isSelected = selectedOption && currency.code === selectedOption;
//       const isDisabled = disabledOption && currency.code === disabledOption;
//
//       const option = document.createElement('option');
//       option.value = currency.code;
//       option.text = `${currency.code} • ${currency.description}`;
//       option.selected = isSelected;
//       option.disabled = isDisabled;
//       selectCurrencyColumnSelect.appendChild(option);
//     });
//   };
//
//   app.listen('config', async config => {
//     const {
//       context: { available_columns: availableColumns },
//       settings,
//     } = config;
//
//     columns = availableColumns;
//
//     const inputColumnSelect = document.getElementById('input-column');
//     const outputColumnInput = document.getElementById('output-column');
//
//     columns.forEach(column => {
//       const isSelected = settings && column.name === settings.from.column;
//       const colLabel = getColumnLabel(column);
//       const option = isSelected ? `<option value="${column.id}" selected>${colLabel}</option>` :
//       `<option value="${column.id}">${colLabel}</option>`;
//
//       inputColumnSelect.innerHTML += option;
//     });
//
//     let selectedToCurrency;
//     let selectedFromCurrency;
//
//     currencies = await getCurrencies();
//
//     if (settings) {
//       outputColumnInput.value = settings.to.column;
//
//       selectedFromCurrency = settings.from.currency;
//       selectedToCurrency = settings.to.currency;
//     } else {
//       [selectedFromCurrency] = [currencies[0].code];
//       [selectedToCurrency] = [currencies[1].code];
//     }
//
//     createCurrencyColumnOptions('from-currency', selectedFromCurrency, selectedToCurrency);
//     createCurrencyColumnOptions('to-currency', selectedToCurrency, selectedFromCurrency);
//
//     hideComponent('loader');
//     showComponent('app');
//
//     const fromCurrency = document.getElementById('from-currency');
//     const toCurrency = document.getElementById('to-currency');
//
//     fromCurrency.addEventListener('change', () => {
//       createCurrencyColumnOptions('to-currency', toCurrency.value, fromCurrency.value);
//     });
//
//     toCurrency.addEventListener('change', () => {
//       createCurrencyColumnOptions('from-currency', fromCurrency.value, toCurrency.value);
//     });
//   });
//
//   app.listen('save', async () => {
//     const data = {
//       settings: [],
//       columns: {
//         input: [],
//         output: [],
//       },
//     };
//
//     const formElements = document.forms.convertCurrency.elements;
//
//     const inputColumnValue = formElements.inputColumn.value;
//     const inputColumn = columns.find(column => column.id === inputColumnValue);
//
//     const outputColumnValue = formElements.outputColumn.value;
//
//     if (outputColumnValue === inputColumn.name) {
//       showError('This fields may not be equal: columns.input.name, columns.output.name.');
//     } else if (outputColumnValue === '' || outputColumnValue === null) {
//       showError('Output column name is required.');
//     } else {
//       const outputColumn = {
//         name: outputColumnValue,
//         type: 'decimal',
//         description: '',
//       };
//
//       const currencyFromValue = formElements.fromCurrency.value;
//       const currencyToValue = formElements.toCurrency.value;
//
//       data.columns.input.push(inputColumn);
//       data.columns.output.push(outputColumn);
//       data.settings.push({
//         from: {
//           currency: currencyFromValue,
//           column: inputColumnValue,
//         },
//         to: {
//           currency: currencyToValue,
//           column: outputColumn.name,
//         },
//       });
//
//       try {
//         const overview = await validate('currency_conversion', data);
//         if (overview.error) {
//           throw new Error(overview.error);
//         }
//         app.emit('save', {
//           data: { ...data, ...overview },
//           status: 'ok',
//         });
//       } catch (e) {
//         showError(e);
//       }
//     }
//   });
// };

createApp({ })
  .then(convert);
