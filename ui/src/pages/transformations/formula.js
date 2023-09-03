/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import suggestBox from '../../libs';
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import '../../../styles/formula.css';
import {
  getColumnLabel,
  getContextVariables,
  getDataFromOutputColumnInput,
  getJQInput,
  validate,
} from '../../utils';
import {
  buildOutputColumnInput,
  hideComponent,
  showComponent,
} from '../../components';


let suggestor = {};

export const createFormulaRow = (
  parent,
  index,
  column,
  formula,
  ignore,
) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  parent.appendChild(item);
  buildOutputColumnInput({
    column,
    index,
    parent: item,
  });

  const formulaInput = document.createElement('div');
  formulaInput.classList.add('input-group', '_mt_12', '_mb_18');
  formulaInput.innerHTML = `
    <label class="label" for="formula-${index}">Formula:</label>
    <textarea materialize id="formula-${index}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
    <input type="checkbox" id="ignore-${index}" name="ignore-errors-${index}"/>
    <label for="ignore-formula-${index}">Ignore errors</label>
  `;
  item.appendChild(formulaInput);
  suggestBox(document.getElementById(`formula-${index}`), suggestor);
  document.getElementById(`ignore-${index}`).checked = ignore || false;
};

export const formula = (app) => {
  if (!app) return;

  hideComponent('loader');
  showComponent('app');

  let rowIndex = 0;
  let availableInputColumns = [];
  let stream = null;

  app.listen('config', (config) => {
    const {
      context: { stream: currentStream, available_columns: availableColumns },
      settings,
      columns: { output: outputColumns },
    } = config;

    availableInputColumns = availableColumns;
    stream = currentStream;
    const variables = getContextVariables(stream);

    suggestor = {
      '.': availableInputColumns.map(col => {
        const colLabel = getColumnLabel(col);

        return {
          title: colLabel,
          value: `."${colLabel}"`,
        };
      }),
      $: variables.map(variable => ({
        title: variable,
        value: `$${variable}`,
      })),
    };

    const content = document.getElementById('content');
    if (settings && settings.expressions) {
      settings.expressions.forEach((expression, i) => {
        const column = outputColumns.find(col => col.name === expression.to);
        rowIndex = i;
        createFormulaRow(
          content,
          rowIndex,
          column,
          expression.formula,
          expression.ignore_errors,
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
      stream,
      columns: {
        input: availableInputColumns,
        output: [],
      },
    };
    const form = document.getElementsByClassName('list-wrapper');

    for (let index = 0; index < form.length; index += 1) {
      const outputColumn = getDataFromOutputColumnInput(index);
      const jqFormula = document.getElementById(`formula-${index}`).value;
      const ignoreErrors = document.getElementById(`ignore-${index}`).checked;
      const expression = {
        to: outputColumn.name,
        formula: jqFormula,
        type: outputColumn.type,
        ignore_errors: ignoreErrors,
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
          columns: availableInputColumns,
        });
        if (inputColumns.error) {
          throw new Error(inputColumns.error);
        } else {
          data.columns.input = inputColumns;
        }
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(formula);
