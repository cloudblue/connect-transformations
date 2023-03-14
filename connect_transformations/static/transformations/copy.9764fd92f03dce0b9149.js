/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 244:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {


// EXTERNAL MODULE: ../install_temp/node_modules/@cloudblueconnect/connect-ui-toolkit/dist/index.js
var dist = __webpack_require__(243);
;// CONCATENATED MODULE: ./ui/src/utils.js

/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
const utils_getSettings = () => fetch('/api/settings').then((response) => response.json());

const utils_getTfns = () => fetch('/api/transformations').then((response) => response.json());

const validate = (data) => fetch('/api/validate/transform_1_copy_row', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

;// CONCATENATED MODULE: ./ui/src/components.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/

// prepare UI components
const components_prepareSettings = (settings) => {
  try {
    return `<p>${JSON.stringify(settings)}</p>`;
  } catch (e) { return ''; }
};

const components_prepareTransformations = (transformations) => {
  try {
    return transformations.reduce((list, transformation) => `${list}<li class="list-item">
        <div class="list-item-content">
          <h4>${transformation.id} - ${transformation.name}</h4>
          <p>${transformation.class_fqn}</p>
          <p>${transformation.status}</p>
          <p>${transformation.description}</p>
        </div>
      </li>`, '');
  } catch (e) { return ''; }
};

// render UI components
const components_renderSettings = (settings) => {
  const element = document.getElementById('settings');
  element.innerHTML = settings;
};

const components_renderTransformations = (transformations) => {
  const element = document.getElementById('transformations');
  element.innerHTML = transformations;
};

// render UI components - show/hide
const components_showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

const components_hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};

;// CONCATENATED MODULE: ./ui/src/pages.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/





const index = async () => {
  hideComponent('app');
  showComponent('loader');
  const tfns = await getTfns();
  const transformations = prepareTransformations(tfns);
  hideComponent('loader');
  showComponent('app');
  renderTransformations(transformations);
};

const settings = async (app) => {
  if (!app) return;
  hideComponent('app');
  showComponent('loader');
  const data = await getSettings();
  const dataSettings = prepareSettings(data);
  renderSettings(dataSettings);
  hideComponent('loader');
  showComponent('app');
};

const tfnMultiplierSettings = (app) => {
  if (!app) return;
  app.listen('config', (config) => {
    // eslint-disable-next-line no-console
    console.log('settings', config);
    const { context: { available_columns: columns } } = config;

    const select = document.getElementById('columns');
    const input = document.getElementById('copy');
    columns.forEach((column) => {
      const { id, name } = column;
      const option = document.createElement('option');
      option.value = id;
      option.text = name;
      select.appendChild(option);
    });

    app.listen('save', async () => {
      const inputColumn = columns.find((column) => column.id === select.value);
      try {
        const overview = await validate({ settings: [
          {
            from: inputColumn.name,
            to: input.value,
          },
        ],
        columns: {
          input: [inputColumn],
          output: [],
        } });
        app.emit('save', { data: { ...{ settings: [
          {
            from: inputColumn.name,
            to: input.value,
          },
        ],
        columns: {
          input: [inputColumn],
          output: [{
            name: input.value,
            type: inputColumn.type,
            description: '',
          }],
        } },
        ...overview },
        status: 'ok' });
      } catch (e) {
        window.alert(e);
      }
    });
  });
  components_hideComponent('app');
  components_showComponent('loader');
  // here you can
  // const columns = [];
  // const transformations = prepareTransformations(tfns);
  components_hideComponent('loader');
  components_showComponent('app');
  // renderTransformations(transformations);
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/copy.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/






(0,dist/* default */.ZP)({ 'main-card': dist/* Card */.Zb })
  .then(tfnMultiplierSettings);


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			61: 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkeaas_e2e_transformations_mock"] = self["webpackChunkeaas_e2e_transformations_mock"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(244)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;