
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
export const getSettings = () => fetch('/api/settings').then((response) => response.json());

export const getTfns = () => fetch('/api/transformations').then((response) => response.json());

export const validate = (data) => fetch('/api/validate/transform_1_copy_row', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());
