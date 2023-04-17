/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import {
  filterRow,
} from '../../pages';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/filter_row.css';


createApp({ })
  .then(filterRow);
