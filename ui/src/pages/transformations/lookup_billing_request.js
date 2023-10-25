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
  getDataFromOutputColumnInput,
  getLookupSubscriptionParameters,
  validate,
} from '../../utils';
import {
  buildOutputColumnInput,
  hideComponent,
  showComponent,
} from '../../components';


const AVAILABLE_BILLING_REQUEST_ATTRS = [
  {
    value: 'id',
    label: 'Billing Request ID',
  },
  {
    value: 'events.created.at',
    label: 'Billing Request created at',
  },
  {
    value: 'events.updated.at',
    label: 'Billing Request updated at',
  },
  {
    value: 'asset.id',
    label: 'Subscription ID',
  },
  {
    value: 'asset.status',
    label: 'Subscription status',
  },
  {
    value: 'asset.external_id',
    label: 'Subscription external id',
  },
  {
    value: 'asset.external_uid',
    label: 'Subscription UID',
  },
  {
    value: 'asset.product.id',
    label: 'Product id',
  },
  {
    value: 'asset.product.name',
    label: 'Product name',
  },
  {
    value: 'asset.product.status',
    label: 'Product status',
  },
  {
    value: 'asset.connection.provider.id',
    label: 'Distributor ID',
  },
  {
    value: 'asset.connection.provider.name',
    label: 'Distributor name',
  },
  {
    value: 'asset.connection.vendor.id',
    label: 'Vendor ID',
  },
  {
    value: 'asset.connection.vendor.name',
    label: 'Vendor name',
  },
  {
    value: 'asset.connection.hub.id',
    label: 'Hub id',
  },
  {
    value: 'asset.connection.hub.name',
    label: 'Hub name',
  },
  {
    value: 'asset.tiers.customer.id',
    label: 'Customer ID',
  },
  {
    value: 'asset.tiers.customer.external_id',
    label: 'Customer external ID',
  },
  {
    value: 'asset.tiers.customer.external_uid',
    label: 'Customer external UID',
  },
  {
    value: 'asset.tiers.customer.name',
    label: 'Customer name',
  },
  {
    value: 'asset.tiers.tier1.id',
    label: 'Tier1 ID',
  },
  {
    value: 'asset.tiers.tier1.external_id',
    label: 'Tier1 external ID',
  },
  {
    value: 'asset.tiers.tier1.external_uid',
    label: 'Tier1 external UID',
  },
  {
    value: 'asset.tiers.tier1.name',
    label: 'Tier1 name',
  },
  {
    value: 'asset.tiers.tier2.id',
    label: 'Tier2 ID',
  },
  {
    value: 'asset.tiers.tier2.external_id',
    label: 'Tier2 external ID',
  },
  {
    value: 'asset.tiers.tier2.external_uid',
    label: 'Tier2 external UID',
  },
  {
    value: 'asset.tiers.tier2.name',
    label: 'Tier2 name',
  },
  {
    value: 'asset.marketplace.id',
    label: 'Marketplace ID',
  },
  {
    value: 'asset.marketplace.name',
    label: 'Marketplace name',
  },
  {
    value: 'asset.contract.id',
    label: 'Contract ID',
  },
  {
    value: 'asset.contract.name',
    label: 'Contract name',
  },
  {
    value: 'asset.parameter.value',
    label: 'Parameter value',
  },
  {
    value: 'items.id',
    label: 'Product item IDs',
  },
  {
    value: 'items.global_id',
    label: 'Product item global IDs',
  },
  {
    value: 'items.mpn',
    label: 'Product item MPNs',
  },
  {
    value: 'items.item_type',
    label: 'Product item types',
  },
  {
    value: 'items.quantity',
    label: 'Product item quantity',
  },
  {
    value: 'items.period',
    label: 'Product item period',
  },
];


const createOutputRow = (parent, index, column, parameters, columnConfigs) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  parent.appendChild(item);

  const columnConfig = columnConfigs?.[column.name];

  const sourceSelect = document.createElement('select');
  sourceSelect.id = `source-select-${index}`;
  sourceSelect.classList.add('output-column-source');

  AVAILABLE_BILLING_REQUEST_ATTRS.forEach(optionData => {
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
    if (sourceSelect.value === 'asset.parameter.value') {
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

const lookupBillingRequest = (app) => {
  if (!app) return;

  let columns = [];
  let parameters = [];

  app.listen('config', async (config) => {
    const {
      columns: { output: outputColumns },
      context: { available_columns: availableColumns, stream },
      settings,
    } = config;
    const outputConfigs = settings?.output_config;
    let rowIndex = 0;

    const hasProduct = 'product' in stream.context;
    columns = availableColumns;
    const criteria = {
      external_id: 'CloudBlue Subscription External ID',
      id: 'CloudBlue Subscription ID',
      skip: 'Skip search by Subscription',
    };

    const item = {
      id: 'Item ID',
      global_id: 'Item Global ID',
      mpn: 'Item MPN',
      all: 'Include all',
    };

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
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    Object.keys(item).forEach((key) => {
      const option = document.createElement('option');
      option.value = key;
      option.text = item[key];
      document.getElementById('item').appendChild(option);
    });

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('item_column').appendChild(option);
    });

    if (hasProduct === true) {
      parameters = await getLookupSubscriptionParameters(stream.context.product.id, 'billing_request');
      parameters.forEach((element) => {
        const option = document.createElement('option');
        option.value = element.id;
        option.text = element.name;
        document.getElementById('parameter').appendChild(option);
      });

      availableColumns.forEach((column) => {
        const option = document.createElement('option');
        option.value = column.id;
        option.text = getColumnLabel(column);
        document.getElementById('parameter_column').appendChild(option);
      });
    }

    if (settings) {
      if (settings.asset_type === null) {
        document.getElementById('criteria').value = 'skip';
        document.getElementById('subscription_column').style.display = 'none';
      } else {
        const columnId = columns.find((c) => c.name === settings.asset_column).id;
        document.getElementById('criteria').value = settings.asset_type || 'skip';
        document.getElementById('column').value = columnId;
      }

      document.getElementById('parameter').value = settings.parameter.id;
      const parameterColId = columns.find((c) => c.name === settings.parameter_column).id;
      document.getElementById('parameter_column').value = parameterColId;

      document.getElementById('item').value = settings.item.id;
      if (['skip', 'all'].includes(settings.item.id)) {
        document.getElementById('item_column_group').style.display = 'none';
      } else {
        const itemId = columns.find((c) => c.name === settings.item_column).id;
        document.getElementById('item_column').value = itemId;
      }

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
    } else {
      document.getElementById('not_found_leave_empty').checked = true;
      document.getElementById('multiple_use_most_actual').checked = true;
    }

    document.getElementById('criteria').addEventListener('change', () => {
      if (document.getElementById('criteria').value === 'skip') {
        document.getElementById('subscription_column').style.display = 'none';
      } else {
        document.getElementById('subscription_column').style.display = 'block';
      }
    });

    document.getElementById('item').addEventListener('change', () => {
      if (document.getElementById('item').value === 'all') {
        document.getElementById('item_column_group').style.display = 'none';
      } else {
        document.getElementById('item_column_group').style.display = 'block';
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
    let assetType = document.getElementById('criteria').value;
    let assetColumn = null;
    if (assetType === 'skip') {
      assetType = null;
    } else {
      assetColumn = columns.find((c) => c.id === document.getElementById('column').value);
    }

    let select = document.getElementById('parameter');
    const parameter = { name: select[select.selectedIndex].text, id: select.value };
    const parameterColumn = columns.find((c) => c.id === document.getElementById('parameter_column').value);

    select = document.getElementById('item');
    const item = { name: select[select.selectedIndex].text, id: select.value };
    const itemColumn = columns.find((c) => c.id === document.getElementById('item_column').value);


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

      if (colSource === 'asset.parameter.value') {
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
        type: 'string',
      });
      outputColumnsConfig[colName] = columnConfig;
    }

    const settings = {
      parameter,
      parameter_column: parameterColumn.name,
      asset_type: assetType,
      asset_column: assetColumn == null ? null : assetColumn.name,
      item,
      item_column: itemColumn.name,
      action_if_not_found: actionIfNotFound,
      action_if_multiple: actionIfMultiple,
      output_config: outputColumnsConfig,
    };
    let inputColumns = [];
    if (assetColumn != null) {
      inputColumns = [assetColumn, itemColumn, parameterColumn];
    } else {
      inputColumns = [itemColumn, parameterColumn];
    }

    const data = {
      settings,
      columns: {
        input: inputColumns,
        output: outputColumnsData,
      },
    };

    try {
      const overview = await validate('lookup_billing_request', data);
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
  .then(lookupBillingRequest);
