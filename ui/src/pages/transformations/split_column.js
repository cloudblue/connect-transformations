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
  getGroups,
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


function getCurrentGroups(parent) {
  const descendents = parent.getElementsByTagName('input');
  const currentGroups = {};
  for (let i = 0; i < descendents.length; i += 1) {
    const element = descendents[i];
    const dataType = document.getElementById(`${element.id}-datatype`);
    if (dataType && dataType.value === 'decimal') {
      const precision = document.getElementById(`${element.id}-precision`).value;
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
  <select id="${groupKey}-datatype">
  <option value="string" selected>String</option>
  <option value="integer">Integer</option>
  <option value="decimal">Decimal</option>
  <option value="boolean">Boolean</option>
  <option value="datetime">Datetime</option>
  </select>
  `;
}

function buildSelectColumnPrecision(groupKey, enabled) {
  return `
  <select id="${groupKey}-precision" ${enabled === true ? '' : 'disabled'}>
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
    const selectPrecision = buildSelectColumnPrecision(groupKey, groupValue.type === 'decimal');
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
    document.getElementById(`${groupKey}-datatype`).value = groupValue.type;
    document.getElementById(`${groupKey}-precision`).value = groupValue.precision;
    document.getElementById(`${groupKey}-datatype`).addEventListener('change', () => {
      if (document.getElementById(`${groupKey}-datatype`).value === 'decimal') {
        document.getElementById(`${groupKey}-precision`).disabled = false;
      } else {
        document.getElementById(`${groupKey}-precision`).disabled = true;
      }
    });
  });
}

export const createGroupRows = async () => {
  const parent = document.getElementById('output');
  const groups = getCurrentGroups(parent);
  const pattern = document.getElementById('pattern').value;
  if (pattern) {
    const body = { pattern, groups };
    const response = await getGroups(body);
    if (response.error) {
      showError(response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    showError('The regular expression is empty');
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
      const dataType = document.getElementById(`${option.id}-datatype`).value;
      data.columns.output.push({
        name: option.value,
        type: dataType,
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
      showError(e);
    }
  });
};

createApp({ })
  .then(splitColumn);
