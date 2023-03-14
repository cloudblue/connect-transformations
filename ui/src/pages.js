/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import {
  getSettings,
  getTfns,
  validate,
} from './utils';

import {
  hideComponent,
  prepareSettings,
  prepareTransformations,
  renderSettings,
  renderTransformations,
  showComponent,
} from './components';


export const index = async () => {
  hideComponent('app');
  showComponent('loader');
  const tfns = await getTfns();
  const transformations = prepareTransformations(tfns);
  hideComponent('loader');
  showComponent('app');
  renderTransformations(transformations);
};

export const settings = async (app) => {
  if (!app) return;
  hideComponent('app');
  showComponent('loader');
  const data = await getSettings();
  const dataSettings = prepareSettings(data);
  renderSettings(dataSettings);
  hideComponent('loader');
  showComponent('app');
};

export const tfnMultiplierSettings = (app) => {
  if (!app) return;
  app.listen('config', (config) => {
    // eslint-disable-next-line no-console
    console.log('settings', config);
    const { context: { available_columns: columns } } = config;

    const select = document.getElementById('columns');
    const input = document.getElementById('copy');
    columns.forEach((column) => {
      const { id, name } = column;
      const option = document.createElement('option');
      option.value = id;
      option.text = name;
      select.appendChild(option);
    });

    app.listen('save', async () => {
      const inputColumn = columns.find((column) => column.id === select.value);
      try {
        const overview = await validate({ settings: [
          {
            from: inputColumn.name,
            to: input.value,
          },
        ],
        columns: {
          input: [inputColumn],
          output: [],
        } });
        app.emit('save', { data: { ...{ settings: [
          {
            from: inputColumn.name,
            to: input.value,
          },
        ],
        columns: {
          input: [inputColumn],
          output: [{
            name: input.value,
            type: inputColumn.type,
            description: '',
          }],
        } },
        ...overview },
        status: 'ok' });
      } catch (e) {
        window.alert(e);
      }
    });
  });
  hideComponent('app');
  showComponent('loader');
  // here you can
  // const columns = [];
  // const transformations = prepareTransformations(tfns);
  hideComponent('loader');
  showComponent('app');
  // renderTransformations(transformations);
};
