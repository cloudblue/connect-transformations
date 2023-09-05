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
  getColumnLabel, getDataFromOutputColumnInput,
  getLookupSubscriptionParameters,
  validate,
} from '../../utils';
import {
  buildOutputColumnInput,
  hideComponent,
  showComponent,
} from '../../components';


const AVAILABLE_SUBSCRIPTION_ATTRS = [
  {
    value: 'id',
    label: 'Subscription ID',
  },
  {
    value: 'status',
    label: 'Subscription status',
  },
  {
    value: 'events.created.at',
    label: 'Subscription created at',
  },
  {
    value: 'events.updated.at',
    label: 'Subscription updated at',
  },
  {
    value: 'external_id',
    label: 'Subscription external id',
  },
  {
    value: 'external_uid',
    label: 'Subscription UID',
  },
  {
    value: 'product.id',
    label: 'Product id',
  },
  {
    value: 'product.name',
    label: 'Product name',
  },
  {
    value: 'product.status',
    label: 'Product status',
  },
  {
    value: 'connection.provider.id',
    label: 'Distributor ID',
  },
  {
    value: 'connection.provider.name',
    label: 'Distributor name',
  },
  {
    value: 'connection.vendor.id',
    label: 'Vendor ID',
  },
  {
    value: 'connection.vendor.name',
    label: 'Vendor name',
  },
  {
    value: 'connection.hub.id',
    label: 'Hub id',
  },
  {
    value: 'connection.hub.name',
    label: 'Hub name',
  },
  {
    value: 'tiers.customer.id',
    label: 'Customer ID',
  },
  {
    value: 'tiers.customer.external_id',
    label: 'Customer external ID',
  },
  {
    value: 'tiers.customer.external_uid',
    label: 'Customer external UID',
  },
  {
    value: 'tiers.customer.name',
    label: 'Customer name',
  },
  {
    value: 'tiers.customer.tax_id',
    label: 'Customer tax ID',
  },
  {
    value: 'tiers.tier1.id',
    label: 'Tier1 ID',
  },
  {
    value: 'tiers.tier1.external_id',
    label: 'Tier1 external ID',
  },
  {
    value: 'tiers.tier1.external_uid',
    label: 'Tier1 external UID',
  },
  {
    value: 'tiers.tier1.name',
    label: 'Tier1 name',
  },
  {
    value: 'tiers.tier1.tax_id',
    label: 'Tier1 tax ID',
  },
  {
    value: 'tiers.tier2.id',
    label: 'Tier2 ID',
  },
  {
    value: 'tiers.tier2.external_id',
    label: 'Tier2 external ID',
  },
  {
    value: 'tiers.tier2.external_uid',
    label: 'Tier2 external UID',
  },
  {
    value: 'tiers.tier2.name',
    label: 'Tier2 name',
  },
  {
    value: 'tiers.tier2.tax_id',
    label: 'Tier2 tax ID',
  },
  {
    value: 'marketplace.id',
    label: 'Marketplace ID',
  },
  {
    value: 'marketplace.name',
    label: 'Marketplace name',
  },
  {
    value: 'contract.id',
    label: 'Contract ID',
  },
  {
    value: 'contract.name',
    label: 'Contract name',
  },
  {
    value: 'billing.period.delta',
    label: 'Billing period delta',
  },
  {
    value: 'billing.period.uom',
    label: 'Billing period uom',
  },
  {
    value: 'parameter.value',
    label: 'Parameter value',
  },
  {
    value: 'items.id',
    label: 'Product item IDs',
  },
];

const SUBSCRIPTION_ATTR_TYPES = {
  'billing.period.delta': 'decimal',
};


const createOutputRow = (parent, index, column, parameters, columnConfigs) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  parent.appendChild(item);

  const columnConfig = columnConfigs?.[column.name];

  const sourceSelect = document.createElement('select');
  sourceSelect.id = `source-select-${index}`;
  sourceSelect.classList.add('output-column-source');

  AVAILABLE_SUBSCRIPTION_ATTRS.forEach(optionData => {
    const option = document.createElement('option');
    option.value = optionData.value;
    option.innerHTML = optionData.label;

    sourceSelect.appendChild(option);
  });
  if (columnConfig) {
    sourceSelect.value = columnConfig.attribute;
  }

  const paramNameSelect = document.createElement('select');
  paramNameSelect.id = `source-param-select-${index}`;

  parameters.forEach(param => {
    const paramOption = document.createElement('option');
    paramOption.value = param.name;
    paramOption.text = param.name;
    paramNameSelect.appendChild(paramOption);
  });
  if (columnConfig?.parameter_name) {
    paramNameSelect.value = columnConfig.parameter_name;
  }

  buildOutputColumnInput({
    column,
    index,
    parent: item,
    additionalInputs: [sourceSelect, paramNameSelect],
    showType: false,
  });

  const handleSourceSelectChange = () => {
    if (sourceSelect.value === 'parameter.value') {
      paramNameSelect.style.display = 'block';
      paramNameSelect.style.maxWidth = 'calc(28% - 10px)';
      sourceSelect.style.maxWidth = 'calc(25% - 10px)';
    } else {
      paramNameSelect.style.display = 'none';
      sourceSelect.style.maxWidth = null;
    }
  };

  handleSourceSelectChange();
  sourceSelect.addEventListener('change', handleSourceSelectChange);
};

const lookupSubscription = (app) => {
  if (!app) return;

  let columns = [];
  let parameters = [];

  app.listen('config', async (config) => {
    const {
      columns: { output: outputColumns },
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;
    const outputConfigs = settings.output_config;
    let rowIndex = 0;

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
      parameters = await getLookupSubscriptionParameters(stream.context.product.id);
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
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('not_found_leave_empty').checked = true;
      } else {
        document.getElementById('not_found_fail').checked = true;
      }
      const multipleInput = document.getElementById(`multiple_${settings.action_if_multiple}`);
      if (multipleInput) {
        multipleInput.checked = true;
      } else {
        document.getElementById('multiple_fail').checked = true;
      }
      if (settings.lookup_type === 'params__value') {
        document.getElementById('parameter').value = settings.parameter.id;
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    } else {
      document.getElementById('param_name_group').style.display = 'none';
      document.getElementById('not_found_leave_empty').checked = true;
      document.getElementById('multiple_use_most_actual').checked = true;
    }

    document.getElementById('criteria').addEventListener('change', () => {
      if (document.getElementById('criteria').value === 'params__value') {
        document.getElementById('param_name_group').style.display = 'block';
      } else {
        document.getElementById('param_name_group').style.display = 'none';
      }
    });

    const outputColumnsElement = document.getElementById('output-columns');

    if (outputColumns.length > 0) {
      outputColumns.forEach((outputColumn, index) => {
        rowIndex = index;
        createOutputRow(outputColumnsElement, rowIndex, outputColumn, parameters, outputConfigs);
      });
    } else {
      createOutputRow(outputColumnsElement, rowIndex, undefined, parameters);
    }
    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createOutputRow(outputColumnsElement, rowIndex, undefined, parameters);
    });
  });

  app.listen('save', async () => {
    const criteria = document.getElementById('criteria').value;
    const columnId = document.getElementById('column').value;
    let parameter = {};
    if (document.getElementById('criteria').value === 'params__value') {
      const select = document.getElementById('parameter');
      const paramName = select[select.selectedIndex].text;
      const paramID = select.value;
      parameter = { name: paramName, id: paramID };
    }
    const column = columns.find((c) => c.id === columnId);
    const actionIfNotFound = document.querySelector('input[name="if_not_found"]:checked').value;
    const actionIfMultiple = document.querySelector('input[name="if_multiple"]:checked').value;

    const outputs = document.getElementsByClassName('output-column-container');
    const outputColumnsData = [];
    const outputColumnsConfig = {};

    for (let i = 0; i < outputs.length; i += 1) {
      const index = outputs[i].id;
      const sourceSelect = document.getElementById(`source-select-${index}`);
      const colSource = sourceSelect.value;
      let colName = getDataFromOutputColumnInput(index).name;
      const columnConfig = {
        attribute: colSource,
      };

      if (colSource === 'parameter.value') {
        const paramName = document.getElementById(`source-param-select-${index}`).value;
        columnConfig.parameter_name = paramName;
      }

      if (!colName) {
        colName = sourceSelect.options[sourceSelect.selectedIndex].label;
        if (columnConfig.parameter_name) {
          colName += ` ${columnConfig.parameter_name}`;
        }
      }

      outputColumnsData.push({
        name: colName,
        type: SUBSCRIPTION_ATTR_TYPES[columnConfig.attribute] || 'string',
      });
      outputColumnsConfig[colName] = columnConfig;
    }

    const data = {
      settings: {
        lookup_type: criteria,
        from: column.name,
        parameter,
        action_if_not_found: actionIfNotFound,
        action_if_multiple: actionIfMultiple,
        output_config: outputColumnsConfig,
      },
      columns: {
        input: [column],
        output: outputColumnsData,
      },
    };

    try {
      const overview = await validate('lookup_subscription', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(lookupSubscription);
