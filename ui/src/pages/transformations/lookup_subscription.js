/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import {
  lookupSubscription,
} from '../../pages';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/lookup.css';


createApp({ })
  .then(lookupSubscription);
