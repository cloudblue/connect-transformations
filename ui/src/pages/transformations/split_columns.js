/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/split_column.css';
import '../../../styles/app.styl';
import {
  getColumnLabel,
  getGroups,
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
} from '../../components';


function getCurrentGroups(parent) {
  const descendents = parent.getElementsByTagName('input');
  const currentGroups = {};
  for (let i = 0; i < descendents.length; i += 1) {
    const element = descendents[i];
    const dataType = document.getElementById(`datatype-${element.id}`);
    if (dataType && dataType.value === 'decimal') {
      const precision = document.getElementById(`precision-${element.id}`).value;
      currentGroups[element.id] = {
        name: element.value,
        type: dataType.value,
        precision,
      };
    } else {
      currentGroups[element.id] = { name: element.value, type: dataType.value };
    }
  }

  return currentGroups;
}

function buildSelectColumnType(groupKey) {
  return `
  <select id="datatype-${groupKey}">
  <option value="string" selected>String</option>
  <option value="integer">Integer</option>
  <option value="decimal">Decimal</option>
  <option value="boolean">Boolean</option>
  <option value="datetime">Datetime</option>
  </select>
  `;
}

function buildSelectColumnPrecision(groupKey) {
  return `
  <select id="precision-${groupKey}">
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

function buildGroups(groups) {
  const parent = document.getElementById('output');
  parent.innerHTML = '';
  if (Object.keys(groups).length > 0) {
    const item = document.createElement('div');
    item.setAttribute('class', 'wrapper output-header');
    item.innerHTML = `
    <div>
    Name
    </div>
    <div>
    Type
    </div>
    <div>
    Precision
    </div>
    `;
    parent.appendChild(item);
  }
  Object.keys(groups).forEach(groupKey => {
    const groupValue = groups[groupKey];
    const item = document.createElement('div');
    item.className = 'wrapper';
    const selectType = buildSelectColumnType(groupKey);
    const selectPrecision = buildSelectColumnPrecision(groupKey);
    item.innerHTML = `
    <div>
    <input 
    type="text" 
    class="output-input" 
    id="${groupKey}"
    placeholder="${groupKey} group name" 
    value="${groupValue.name}"/>
    </div>
    <div>
    ${selectType}
    </div>
    <div>
    ${selectPrecision}
    </div>
    `;
    parent.appendChild(item);
    document.getElementById(`datatype-${groupKey}`).value = groupValue.type;
    const precisionSelect = document.getElementById(`precision-${groupKey}`);
    precisionSelect.disabled = groupValue.type !== 'decimal';
    precisionSelect.value = groupValue.precision || '2';
    document.getElementById(`datatype-${groupKey}`).addEventListener('change', () => {
      if (document.getElementById(`datatype-${groupKey}`).value === 'decimal') {
        document.getElementById(`precision-${groupKey}`).disabled = false;
      } else {
        document.getElementById(`precision-${groupKey}`).disabled = true;
      }
    });
  });
}

export const createGroupRows = async (app) => {
  const parent = document.getElementById('output');
  const groups = getCurrentGroups(parent);
  const pattern = document.getElementById('pattern').value;
  app.emit('validation-error', '');
  if (pattern) {
    const body = { pattern, groups };
    const response = await getGroups(body);
    if (response.error) {
      app.emit('validation-error', response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    app.emit('validation-error', 'The regular expression is empty');
  }
};

export const splitColumn = (app) => {
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
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('pattern').value = settings.regex.pattern;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      buildGroups(settings.regex.groups);
    }

    document.getElementById('refresh').addEventListener('click', () => {
      createGroupRows(app);
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
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    data.columns.input.push(inputColumn);

    const selector = document.getElementById('output');
    const options = selector.getElementsByTagName('input');
    for (let i = 0; i < options.length; i += 1) {
      const option = options[i];
      const dataType = document.getElementById(`datatype-${option.id}`).value;
      const outputColumn = {
        name: option.value,
        type: dataType,
        description: '',
        constraints: {},
      };
      if (dataType === 'decimal') {
        const precision = document.getElementById(`precision-${option.id}`).value;
        outputColumn.constraints = { precision: parseInt(precision, 10) };
      }
      data.columns.output.push(outputColumn);
    }

    data.settings = {
      from: inputColumn.name,
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
      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(splitColumn);
