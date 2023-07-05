/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/lookup.css';
import '../../../styles/app.styl';
import {
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


export const createOutputColumnForLookup = (prefix, name) => ({
  name: `${prefix}.${name}`,
  type: 'string',
  description: '',
});

export const lookupProductItem = (app) => {
  if (!app) return;

  let columns = [];
  const toggleProductId = (value) => {
    if (value === 'product_id') {
      hideComponent('product_column_input');
      showComponent('product_id_input');
    } else {
      hideComponent('product_id_input');
      showComponent('product_column_input');
    }
  };

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = {
      mpn: 'CloudBlue Item MPN',
      id: 'CloudBlue Item ID',
    };

    // defaults
    document.getElementById('leave_empty').checked = true;
    document.getElementById('by_product_id').checked = true;
    hideComponent('product_column_input');
    showComponent('product_id_input');
    hideComponent('loader');
    showComponent('app');

    Object.keys(criteria).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = criteria[key];
      document.getElementById('criteria').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = column.name;
      document.getElementById('column').appendChild(option);

      const anotherOption = document.createElement('option');
      anotherOption.value = column.id;
      anotherOption.text = column.name;
      document.getElementById('product_id_column').appendChild(anotherOption);
    });

    if (hasProduct === true) {
      document.getElementById('product_id').value = stream.context.product.id;
      hideComponent('product_id_input');
      hideComponent('product_column_input');
      hideComponent('product_id_radio_group');
      hideComponent('no_product');
    }

    if (settings) {
      document.getElementById('product_id').value = settings.product_id;
      document.getElementById('criteria').value = settings.lookup_type;
      document.getElementById('column').value = columns.find((c) => c.name === settings.from).id;
      document.getElementById('product_id_column').value = columns.find((c) => c.name === settings.product_column).id;
      document.getElementById('prefix').value = settings.prefix;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('leave_empty').checked = true;
      } else {
        document.getElementById('fail').checked = true;
      }
      if (settings.product_lookup_mode === 'id') {
        document.getElementById('by_product_id').checked = true;
        hideComponent('product_column_input');
        showComponent('product_id_input');
      } else {
        document.getElementById('by_product_column').checked = true;
        hideComponent('product_id_input');
        showComponent('product_column_input');
      }
    }

    const radios = document.getElementsByName('product_id_radio');
    for (let i = 0, max = radios.length; i < max; i += 1) {
      radios[i].onclick = () => {
        toggleProductId(radios[i].value);
      };
    }
  });

  app.listen('save', async () => {
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    const prefix = document.getElementById('prefix').value;
    const column = columns.find((c) => c.id === columnId);
    const actionIfNotFound = document.getElementById('leave_empty').checked ? 'leave_empty' : 'fail';
    const productLookupMode = document.getElementById('by_product_id').checked ? 'id' : 'column';
    const productId = document.getElementById('product_id').value;
    const productColumnId = document.getElementById('product_id_column').value;
    const productColumn = columns.find((c) => c.id === productColumnId);

    const input = [column];
    if (productLookupMode === 'column') {
      input.push(productColumn);
    }

    const data = {
      settings: {
        product_id: productId,
        lookup_type: criteria,
        from: column.name,
        prefix,
        action_if_not_found: actionIfNotFound,
        product_column: productColumn?.name ?? '',
        product_lookup_mode: productLookupMode,
      },
      columns: {
        input,
        output: [
          'product.id',
          'product.name',
          'item.id',
          'item.name',
          'item.unit',
          'item.period',
          'item.mpn',
          'item.commitment',
        ].map((name) => createOutputColumnForLookup(prefix, name)),
      },
    };

    try {
      const overview = await validate('lookup_product_item', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

createApp({ })
  .then(lookupProductItem);
