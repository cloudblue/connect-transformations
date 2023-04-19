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
  getLookupProductItemCriteria,
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

  app.listen('config', async (config) => {
    const {
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = await getLookupProductItemCriteria();

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
    }

    if (settings) {
      document.getElementById('product_id').value = settings.product_id;
      document.getElementById('criteria').value = settings.lookup_type;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      const productColumnId = columns.find((c) => c.name === settings.product_column).id;
      document.getElementById('column').value = productColumnId;
      document.getElementById('prefix').value = settings.prefix;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('leave_empty').checked = true;
      } else {
        document.getElementById('fail').checked = true;
      }
    } else {
      document.getElementById('param_name_group').style.display = 'none';
      document.getElementById('leave_empty').checked = true;
    }
  });

  app.listen('save', async () => {
    const productId = document.getElementById('product_id').value;
    const productColumnId = document.getElementById('product_id_column').value;
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    const prefix = document.getElementById('prefix').value;
    const column = columns.find((c) => c.id === columnId);
    const productColumn = columns.find((c) => c.id === productColumnId);
    const actionIfNotFound = document.getElementById('leave_empty').checked ? 'leave_empty' : 'fail';

    const input = [column];
    if (productColumnId !== '') {
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
