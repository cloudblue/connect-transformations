
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
export const validate = (functionName, data) => fetch(`/api/validate/${functionName}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

export const getLookupSubscriptionCriteria = () => fetch('/api/lookup_subscription/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
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

