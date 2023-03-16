
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
export const validate = (data) => fetch('/api/validate/copy_columns', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());
