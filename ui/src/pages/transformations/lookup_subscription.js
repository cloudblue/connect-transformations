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
  getColumnLabel,
  getLookupSubscriptionParameters,
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

export const lookupSubscription = (app) => {
  if (!app) return;

  let columns = [];

  app.listen('config', async (config) => {
    const {
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = {
      external_id: 'CloudBlue Subscription External ID',
      id: 'CloudBlue Subscription ID',
      params__value: 'Parameter Value',
    };

    hideComponent('loader');
    showComponent('app');

    Object.keys(criteria).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = criteria[key];
      if (hasProduct === false && key === 'params__value') {
        option.disabled = true;
      }
      document.getElementById('criteria').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    if (hasProduct === true) {
      const parameters = await getLookupSubscriptionParameters(stream.context.product.id);
      parameters.forEach((element) => {
        const option = document.createElement('option');
        option.value = element.id;
        option.text = element.name;
        document.getElementById('parameter').appendChild(option);
      });
    }

    if (settings) {
      document.getElementById('criteria').value = settings.lookup_type;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      document.getElementById('prefix').value = settings.prefix;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('leave_empty').checked = true;
      } else {
        document.getElementById('fail').checked = true;
      }
      if (settings.lookup_type === 'params__value') {
        document.getElementById('parameter').value = settings.parameter.id;
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    } else {
      document.getElementById('param_name_group').style.display = 'none';
      document.getElementById('leave_empty').checked = true;
    }

    document.getElementById('criteria').addEventListener('change', () => {
      if (document.getElementById('criteria').value === 'params__value') {
        document.getElementById('param_name_group').style.display = 'block';
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    });
  });

  app.listen('save', async () => {
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    const prefix = document.getElementById('prefix').value;
    let parameter = {};
    if (document.getElementById('criteria').value === 'params__value') {
      const select = document.getElementById('parameter');
      const paramName = select[select.selectedIndex].text;
      const paramID = select.value;
      parameter = { name: paramName, id: paramID };
    }
    const column = columns.find((c) => c.id === columnId);
    const actionIfNotFound = document.getElementById('leave_empty').checked ? 'leave_empty' : 'fail';

    const data = {
      settings: {
        lookup_type: criteria,
        from: column.name,
        parameter,
        prefix,
        action_if_not_found: actionIfNotFound,
      },
      columns: {
        input: [column],
        output: [
          'product.id',
          'product.name',
          'marketplace.id',
          'marketplace.name',
          'vendor.id',
          'vendor.name',
          'subscription.id',
          'subscription.external_id',
        ].map((name) => createOutputColumnForLookup(prefix, name)),
      },
    };

    try {
      const overview = await validate('lookup_subscription', data);
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
  .then(lookupSubscription);
