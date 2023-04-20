/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import {
  getJQInput,
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


export const createFormulaRow = (parent, index, output, formula, columnId) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <input type="text" placeholder="Output column" style="width: 70%;" ${output ? `value="${output}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
      <div class="input-group">
          <label class="label" for="${columnId || `formula-${index}`}">Formula:</label>
          <textarea id="${columnId || `formula-${index}`}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
      </div>
    `;
  parent.appendChild(item);
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

export const formula = (app) => {
  if (!app) return;

  hideComponent('loader');
  showComponent('app');

  let rowIndex = 0;
  let columns = [];
  let columnId = '';

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
        columnId = columns.find(col => col.name === expression.to).id;
        createFormulaRow(content, rowIndex, expression.to, expression.formula, columnId);
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
      const jqColumn = line.getElementsByTagName('textarea')[0].id;

      const outputColumn = {
        name: to,
        type: 'string',
        nullable: true,
      };
      if (!jqColumn.startsWith('formula-')) {
        outputColumn.id = jqColumn;
      }
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
      showError(e);
    }
  });
};

createApp({ })
  .then(formula);
