/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import {
  convert,
} from '../../pages';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';


createApp({ })
  .then(convert);
