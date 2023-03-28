/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import {
  splitColumn,
} from '../../pages';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/split_column.css';


createApp({ })
  .then(splitColumn);
