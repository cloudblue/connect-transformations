
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
export const validate = (functionName, data) => fetch(`/api/${functionName}/validate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

export const getLookupSubscriptionParameters = (productId) => fetch(`/api/lookup_subscription/parameters?product_id=${productId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

export const getCurrencies = () => fetch('/api/currency_conversion/currencies').then(response => response.json());

/* The data should contain pattern (and optionally groups) keys.
We expect the return groups key (with the new keys found in the regex) and the order
 (to display in order on the UI) */
export const getGroups = (data) => fetch('/api/split_column/extract_groups', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());


/* The data should contain list of jq expressions and all input columns.
We expect to return columns used in expressions */
export const getJQInput = (data) => fetch('/api/formula/extract_input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

/* The data should contain list of attached files. */
export const getAttachments = (streamId) => fetch(`/api/attachment_lookup/${streamId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable */
export const getAirtableBases = (key) => fetch(`/api/airtable_lookup/bases?api_key=${key}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable and the base id is the id of the base */
export const getAirtableTables = (key, baseId) => fetch(`/api/airtable_lookup/tables?api_key=${key}&base_id=${baseId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

export const getColumnLabel = (column) => {
  const colIdParts = column.id.split('-');
  const colIdSuffix = colIdParts[colIdParts.length - 1];

  return `${column.name} (C${colIdSuffix})`;
};

const flattenObj = (ob, prefix) => {
  const result = {};

  Object.keys(ob).forEach((i) => {
    if ((typeof ob[i]) === 'object' && !Array.isArray(ob[i])) {
      const temp = flattenObj(ob[i], '');
      Object.keys(temp).forEach((j) => {
        result[`${prefix}${i}.${j}`] = temp[j];
      });
    } else {
      result[i] = ob[i];
    }
  });

  return result;
};

export const getContextVariables = (stream) => {
  const variables = Object.keys(flattenObj(stream.context, 'context.'));
  if (stream.context?.pricelist) {
    variables.push('context.pricelist_version.id');
    variables.push('context.pricelist_version.start_at');
  }

  if (stream.type === 'billing') {
    variables.push('context.period.start');
    variables.push('context.period.end');
  }

  return variables;
};


export const getDataFromOutputColumnInput = (index) => {
  const data = {
    name: document.getElementById(`name-${index}`).value,
    type: document.getElementById(`type-${index}`).value,
    constraints: {},
  };

  const precision = document.getElementById(`precision-${index}`).value;
  if (data.type === 'decimal' && precision !== 'auto') {
    data.constraints.precision = precision;
  }

  return data;
};
