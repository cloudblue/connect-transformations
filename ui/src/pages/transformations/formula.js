/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import suggestBox from 'suggest-box';
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import '../../../styles/formula.css';
import {
  getJQInput,
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


let suggestor = {};

function buildSelectColumnType(index) {
  return `
  <select id="datatype-${index}">
  <option value="string" selected>String</option>
  <option value="integer">Integer</option>
  <option value="decimal">Decimal</option>
  <option value="boolean">Boolean</option>
  <option value="datetime">Datetime</option>
  </select>
  `;
}

function buildSelectColumnPrecision(index) {
  return `
  <select id="precision-${index}">
  <option value="2" selected>2 decimals</option>
  <option value="3">3 decimals</option>
  <option value="4">4 decimals</option>
  <option value="5">5 decimals</option>
  <option value="6">6 decimals</option>
  <option value="7">7 decimals</option>
  <option value="8">8 decimals</option>
  </select>
  `;
}

export const createFormulaRow = (parent, index, output, columnId, formula, dataType, precision) => {
  const item = document.createElement('div');
  const typeSelect = buildSelectColumnType(index);
  const precisionSelect = buildSelectColumnPrecision(index);
  const columnIdInput = columnId === undefined ? '' : `<input type="text" id="columnid-${index}" value="${columnId}" hidden/>`;
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <div class="output-group">
      ${columnIdInput}
      <input id="output-${index}" type="text" placeholder="Output column" ${output ? `value="${output}"` : ''} />
      ${typeSelect}
      ${precisionSelect}
      <button id="delete-${index}" class="button delete-button">DELETE</button>
      </div>
      <div class="input-group _mt_12 _mb_18">
          <label class="label" for="formula-${index}">Formula:</label>
          <textarea materialize id="formula-${index}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
      </div>
    `;
  parent.appendChild(item);
  suggestBox(document.getElementById(`formula-${index}`), suggestor);
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
  document.getElementById(`datatype-${index}`).value = dataType || 'string';
  document.getElementById(`precision-${index}`).value = precision || '2';
  document.getElementById(`precision-${index}`).disabled = dataType !== 'decimal';
  document.getElementById(`datatype-${index}`).addEventListener('change', () => {
    if (document.getElementById(`datatype-${index}`).value === 'decimal') {
      document.getElementById(`precision-${index}`).disabled = false;
    } else {
      document.getElementById(`precision-${index}`).disabled = true;
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

export const formula = (app) => {
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
    suggestor = { '.': availableColumns.map(col => ({
      title: col.name,
      value: `."${col.name}"`,
    })) };

    const content = document.getElementById('content');
    if (settings && settings.expressions) {
      settings.expressions.forEach((expression, i) => {
        const columnId = columns.find(col => col.name === expression.to).id;
        rowIndex = i;
        createFormulaRow(
          content,
          rowIndex,
          expression.to,
          columnId,
          expression.formula,
          expression.type,
          expression.precision,
        );
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

    for (let iteration = 0; iteration < form.length; iteration += 1) {
      const index = form[iteration].id.split('-')[1];
      const columnIdInput = document.getElementById(`columnid-${index}`);
      const to = document.getElementById(`output-${index}`).value;
      const dataType = document.getElementById(`datatype-${index}`).value;
      const jqFormula = document.getElementById(`formula-${index}`).value;
      const expression = {
        to,
        formula: jqFormula,
        type: dataType,
      };
      const outputColumn = {
        name: to,
        type: dataType,
        nullable: true,
        constraints: {},
      };
      if (dataType === 'decimal') {
        const precision = document.getElementById(`precision-${index}`).value;
        expression.precision = precision;
        outputColumn.constraints = { precision: parseInt(precision, 10) };
      }
      if (columnIdInput) {
        outputColumn.id = columnIdInput.value;
      }
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
      showError(e);
    }
  });
};

createApp({ })
  .then(formula);
