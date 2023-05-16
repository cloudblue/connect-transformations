/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 410:
/***/ ((__unused_webpack_module, exports) => {


function whitespace (s) {
    return /\S/.test(s)
  }
  
  exports.START = exports.END = -1
  
  var start = exports.start = function (text, i, bound) {
    var s = i, S = -1
    while(s >= 0 && bound(text[s])) S = s--
    return exports.START = S
  }
  
  var end = exports.end = function (text, i, bound) {
    var s = i, S = -1
    while(s < text.length && bound(text[s])) S = ++s
    return exports.END = S
  }
  
  var word = exports.word = function (text, i, bound) {
    bound = bound || whitespace
    return text.substring(start(text, i, bound), end(text, i, bound))
  }
  
  exports.replace = function replace (value, text, i, bound) {
    bound = bound || whitespace
  
    var w = word(text, i, bound)
    if(!w) return text
  
    return (
      text.substring(0, exports.START)
    + value
    + text.substring(exports.END)
    )
  }
  

/***/ }),

/***/ 243:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";

var h = __webpack_require__(789)
var wordBoundary = /\s/
var bounds = __webpack_require__(410)

var TextareaCaretPosition = __webpack_require__(969)

var Suggester = __webpack_require__(225)

module.exports = function(el, choices, options) {
  var tcp = new TextareaCaretPosition(el)

  var suggest = Suggester(choices)

  options = options || {}

  var stringify = options.stringify || String

  var box = {
    input: el,
    choices: choices,
    options: options,
    active: false,
    activate: activate,
    deactivate: deactivate,
    selection: 0,
    filtered: [],

    //get the current word
    get: function (i) {
      i = Number.isInteger(i) ? i : el.selectionStart - 1
      return bounds.word(el.value, i)
    },

    //replace the current word
    set: function (w, i) {
      i = Number.isInteger(i) ? i : el.selectionStart - 1
      el.value = bounds.replace(w, el.value + ' ', i)
      el.selectionStart = el.selectionEnd = bounds.START + w.length + 1
    },

    select: function (n) {
      this.selection = Math.max(0, Math.min(this.filtered.length, n))
      this.update()
    },
    next: function () {
      this.select(this.selection + 1)
    },
    prev: function () {
      this.select(this.selection - 1)
    },
    suggest: function (cb) {
      var choices, self = this
      // extract current word
      var word = this.get()
      if(!word)
        return this.deactivate(), cb()

      // filter and order the list by the current word
      this.selection = 0

      var r = this.request = (this.request || 0) + 1
      suggest(word, function (err, choices) {
        if(err) return console.error(err)
        if(r !== self.request) return cb()
        if(choices) cb(null, self.filtered = choices)
      })

    },
    reposition: function () {
      self = this
      if (self.filtered.length == 0)
        return self.deactivate()

      // create / update the element
      if (self.active) {
        self.update()
      } else {
        // calculate position
        var pos = tcp.get(el.selectionStart, el.selectionEnd)

        var bounds = el.getBoundingClientRect()
        // setup
        self.x = pos.left + bounds.left - el.scrollLeft
        self.y = pos.top + bounds.top - el.scrollTop + 20
        self.activate()
      }
    },
    update: update,
    complete: function (n) {
      if(!isNaN(n)) this.select(n)
      if (this.filtered.length) {
        var choice = this.filtered[this.selection]
        if (choice && choice.value) {
          // update the text under the cursor to have the current selection's value          var v = el.value
          this.set(stringify(choice.value))
          // fire the suggestselect event
          el.dispatchEvent(new CustomEvent('suggestselect', { detail: choice }))
        }
      }
      this.deactivate()
    },
  }
  el.addEventListener('input', oninput.bind(box))
  el.addEventListener('keydown', onkeydown.bind(box))
  el.addEventListener('blur', onblur.bind(box))
  return box
}

function getItemIndex(e) {
  for (var el = e.target; el && el != this; el = el.parentNode)
    if (el._i != null)
      return el._i
}

function onListMouseMove(e) {
  this.isMouseActive = true
}

function onListMouseOver(e) {
  // ignore mouseover triggered by list redrawn under the cursor
  if (!this.isMouseActive) return

  var i = getItemIndex(e)
  if (i != null && i != this.selection)
    this.select(i)
}

function onListMouseDown(e) {
  var i = getItemIndex(e)
  if (i != null) {
    this.select(i)
    this.complete()
    // prevent blur
    e.preventDefault()
  }
}

function render(box) {
  var cls = (box.options.cls) ? ('.'+box.options.cls) : ''
  var style = { left: (box.x+'px'), position: 'fixed' }

  // hang the menu above or below the cursor, wherever there is more room
  if (box.y < window.innerHeight/2) {
    style.top = box.y + 'px'
  } else {
    style.bottom = (window.innerHeight - box.y + 20) + 'px'
  }

  return h('.suggest-box'+cls, { style: style }, [
    h('ul', {
      onmousemove: onListMouseMove.bind(box),
      onmouseover: onListMouseOver.bind(box),
      onmousedown: onListMouseDown.bind(box)
    }, renderOpts(box))
  ])
}

function renderOpts(box) {
  var fragment = document.createDocumentFragment()
  for (var i=0; i < box.filtered.length; i++) {
    var opt = box.filtered[i]
    var tag = 'li'
    if (i === box.selection) tag += '.selected'
    if (opt.cls) tag += '.' + opt.cls
    var title = null
    var image = null
    if(opt.showBoth){
        title = h('strong', opt.title)
        image = h('img', { src: opt.image })
    } else title = opt.image ? h('img', { src: opt.image }) : h('strong', opt.title)
    fragment.appendChild(h(tag, {_i: i}, image, ' ', [title, ' ', opt.subtitle && h('small', opt.subtitle)]))
  }
  return fragment
}

function activate() {
  if (this.active)
    return
  this.active = true
  this.el = render(this)
  document.body.appendChild(this.el)
  adjustPosition.call(this)
}

function update() {
  if (!this.active)
    return
  var ul = this.el.querySelector('ul')
  ul.innerHTML = ''
  ul.appendChild(renderOpts(this))
  adjustPosition.call(this)
}

function deactivate() {
  if (!this.active)
    return
  this.el.parentNode.removeChild(this.el)
  this.el = null
  this.active = false
}

function oninput(e) {
  var self = this
  var word = this.suggest(function (_, suggestions) {
    if(suggestions) self.reposition()
  })
}

function onkeydown(e) {
  if (this.active) {
    // escape
    if (e.keyCode == 27) this.deactivate()
    // enter or tab

    else if (e.keyCode == 13 || e.keyCode == 9) this.complete()
    else return //ordinary key, fall back.

    e.preventDefault() //movement key, as above.

    this.isMouseActive = false
  }
}

function onblur(e) {
  this.deactivate()
}

function adjustPosition() {
  // move the box left to fit in the viewport, if needed
  var width = this.el.getBoundingClientRect().width
  var rightOverflow = this.x + width - window.innerWidth
  var rightAdjust = Math.min(this.x, Math.max(0, rightOverflow))
  this.el.style.left = (this.x - rightAdjust) + 'px'
}


/***/ }),

/***/ 225:
/***/ ((module) => {


function isObject (o) {
    return o && 'object' === typeof o
  }
  
  var isArray = Array.isArray
  
  function isFunction (f) {
    return 'function' === typeof f
  }
  
  function compare(a, b) {
    return compareval(a.rank, b.rank) || compareval(a.title, b.title)
  }
  
  function compareval(a, b) {
    return a === b ? 0 : a < b ? -1 : 1
  }
  
  function suggestWord (word, choices, cb) {
    if(isArray(choices)) {
      //remove any non word characters and make case insensitive.
      var wordRe = new RegExp(word.replace(/\W/g, ''), 'i')
      cb(null, choices.map(function (opt, i) {
        var title = wordRe.exec(opt.title)
        var subtitle = opt.subtitle ? wordRe.exec(opt.subtitle) : null
        var rank = (title === null ? (subtitle&&subtitle.index) : (subtitle === null ? (title&&title.index) : Math.min(title.index, subtitle.index)))
        if (rank !== null) {
          opt.rank = rank
          return opt
        }
      }).filter(Boolean).sort(compare).slice(0, 20))
    }
    else if(isFunction(choices)) choices(word, cb)
  }
  
  module.exports = function (choices) {
    if(isFunction(choices)) return choices
  
    else if(isObject(choices) && (choices.any || isArray(choices)))
      return function (word, cb) {
        suggestWord(word, choices.any || choices, cb)
      }
    else if(isObject(choices)) {
      var _choices = choices
      //legacy
      return function (word, cb) {
        if(!choices[word[0]]) return cb()
        suggestWord(word.substring(1), choices[word[0]], cb)
      }
    }
  }
  
  
  
  
  
  
  
  
  
  
  
  

/***/ }),

/***/ 506:
/***/ ((__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) => {

"use strict";

// UNUSED EXPORTS: createFormulaRow, formula

// EXTERNAL MODULE: ./ui/src/libs/index.js
var libs = __webpack_require__(243);
var libs_default = /*#__PURE__*/__webpack_require__.n(libs);
// EXTERNAL MODULE: ./node_modules/@cloudblueconnect/connect-ui-toolkit/dist/index.js
var dist = __webpack_require__(164);
;// CONCATENATED MODULE: ./ui/src/utils.js

/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
// API calls to the backend
/* eslint-disable import/prefer-default-export */
const validate = (functionName, data) => fetch(`/api/validate/${functionName}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

const getLookupSubscriptionCriteria = () => fetch('/api/lookup_subscription/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getLookupProductItemCriteria = () => fetch('/api/lookup_product_item/criteria', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getLookupSubscriptionParameters = (productId) => fetch(`/api/lookup_subscription/parameters?product_id=${productId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

const getCurrencies = () => fetch('/api/currency_conversion/currencies').then(response => response.json());

/* The data should contain pattern (and optionally groups) keys.
We expect the return groups key (with the new keys found in the regex) and the order
 (to display in order on the UI) */
const getGroups = (data) => fetch('/api/split_column/extract_groups', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());


/* The data should contain list of jq expressions and all input columns.
We expect to return columns used in expressions */
const getJQInput = (data) => fetch('/api/formula/extract_input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
}).then((response) => response.json());

/* The data should contain list of attached files. */
const getAttachments = (streamId) => fetch(`/api/attachment_lookup/${streamId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable */
const getAirtableBases = (key) => fetch(`/api/airtable_lookup/bases?api_key=${key}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());

/* The key is the api key from airtable and the base id is the id of the base */
const getAirtableTables = (key, baseId) => fetch(`/api/airtable_lookup/tables?api_key=${key}&base_id=${baseId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
}).then((response) => response.json());


;// CONCATENATED MODULE: ./ui/src/components.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/

// render UI components - show/hide
const showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

const hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};

const showError = (message) => {
  const oldError = document.getElementById('error');
  if (oldError) {
    oldError.remove();
  }
  const error = document.createElement('div');
  error.id = 'error';
  error.innerHTML = `<div class="c-alert">${message}</div>`;
  document.getElementsByTagName('body')[0].appendChild(error);
  document.getElementById('error').scrollIntoView();
};

const hideError = () => {
  const error = document.getElementById('error');
  if (error) {
    error.remove();
  }
};

const getAddSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M19 13H13v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>';

const getDeleteSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M0 0h24v24H0V0z" fill="none"/><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12 1.41 1.41L13.41 14l2.12 2.12-1.41 1.41L12 15.41l-2.12 2.12-1.41-1.41L10.59 14l-2.13-2.12zM15.5 4l-1-1h-5l-1 1H5v2h14V4z"/></svg>';

const getAddButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('add-button');
  button.id = 'add-button';
  button.setAttribute('data-row-index', index);
  button.innerHTML = getAddSvg();

  return button;
};

const getDeleteButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('delete-button');
  button.id = `delete-${index}`;
  button.setAttribute('data-row-index', index);
  button.innerHTML = getDeleteSvg();

  return button;
};

;// CONCATENATED MODULE: ./ui/src/pages/transformations/formula.js
/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/










let suggestor = {};

function buildSelectColumnType(index) {
  return `
  <select id="datatype-${index}">
  <option value="string" selected>String</option>
  <option value="integer">Integer</option>
  <option value="decimal">Decimal</option>
  <option value="boolean">Boolean</option>
  <option value="datetime">Datetime</option>
  </select>
  `;
}

function buildSelectColumnPrecision(index) {
  return `
  <select id="precision-${index}">
  <option value="auto" selected>Auto</option>
  <option value="1">1 decimal</option>
  <option value="2">2 decimals</option>
  <option value="3">3 decimals</option>
  <option value="4">4 decimals</option>
  <option value="5">5 decimals</option>
  <option value="6">6 decimals</option>
  <option value="7">7 decimals</option>
  <option value="8">8 decimals</option>
  </select>
  `;
}

const createFormulaRow = (
  parent,
  index,
  output,
  columnId,
  formula,
  ignore,
  dataType,
  precision,
) => {
  const item = document.createElement('div');
  const typeSelect = buildSelectColumnType(index);
  const precisionSelect = buildSelectColumnPrecision(index);
  const columnIdInput = columnId === undefined ? '' : `<input type="text" id="columnid-${index}" value="${columnId}" hidden/>`;
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <div class="output-group">
      ${columnIdInput}
      <input id="output-${index}" type="text" placeholder="Output column" ${output ? `value="${output}"` : ''} />
      ${typeSelect}
      ${precisionSelect}
      <button id="delete-${index}" class="button delete-button">DELETE</button>
      </div>
      <div class="input-group _mt_12 _mb_18">
          <label class="label" for="formula-${index}">Formula:</label>
          <textarea materialize id="formula-${index}" style="width: 100%;">${formula ? `${formula}` : ''}</textarea>
          <input type="checkbox" id="ignore-${index}" name="ignore-errors-${index}"/>
          <label for="ignore-formula-${index}">Ignore errors</label>
      </div>
      
    `;
  parent.appendChild(item);
  libs_default()(document.getElementById(`formula-${index}`), suggestor);
  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      showError('You need to have at least one row');
    } else {
      document.getElementById(`wrapper-${index}`).remove();
      const buttons = document.getElementsByClassName('delete-button');
      if (buttons.length === 1) {
        buttons[0].disabled = true;
      }
    }
  });
  document.getElementById(`datatype-${index}`).value = dataType || 'string';
  document.getElementById(`ignore-${index}`).checked = ignore || false;

  document.getElementById(`precision-${index}`).value = precision || 'auto';
  document.getElementById(`precision-${index}`).disabled = dataType !== 'decimal';
  document.getElementById(`datatype-${index}`).addEventListener('change', () => {
    if (document.getElementById(`datatype-${index}`).value === 'decimal') {
      document.getElementById(`precision-${index}`).disabled = false;
    } else {
      document.getElementById(`precision-${index}`).disabled = true;
    }
  });
  const buttons = document.getElementsByClassName('delete-button');
  for (let i = 0; i < buttons.length; i += 1) {
    if (buttons.length === 1) {
      buttons[i].disabled = true;
    } else {
      buttons[i].disabled = false;
    }
  }
};

const formula = (app) => {
  if (!app) return;

  hideComponent('loader');
  showComponent('app');

  let rowIndex = 0;
  let columns = [];

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;
    /* eslint-disable-next-line */
    const pattern = /[ .,|*:;{}[\]+\/%]/;
    suggestor = { '.': availableColumns.map(col => {
      const needsQuotes = pattern.test(col.name);

      return {
        title: col.name,
        value: needsQuotes ? `."${col.name}"` : `.${col.name}`,
      };
    }) };

    const content = document.getElementById('content');
    if (settings && settings.expressions) {
      settings.expressions.forEach((expression, i) => {
        const columnId = columns.find(col => col.name === expression.to).id;
        rowIndex = i;
        createFormulaRow(
          content,
          rowIndex,
          expression.to,
          columnId,
          expression.formula,
          expression.ignore_errors,
          expression.type,
          expression.precision,
        );
      });
    } else {
      createFormulaRow(content, rowIndex);
    }
    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createFormulaRow(content, rowIndex);
    });
  });

  app.listen('save', async () => {
    const data = {
      settings: { expressions: [] },
      columns: {
        input: columns,
        output: [],
      },
    };
    const form = document.getElementsByClassName('list-wrapper');

    for (let iteration = 0; iteration < form.length; iteration += 1) {
      const index = form[iteration].id.split('-')[1];
      const columnIdInput = document.getElementById(`columnid-${index}`);
      const to = document.getElementById(`output-${index}`).value;
      const dataType = document.getElementById(`datatype-${index}`).value;
      const jqFormula = document.getElementById(`formula-${index}`).value;
      const ignoreErrors = document.getElementById(`ignore-${index}`).checked;
      const expression = {
        to,
        formula: jqFormula,
        type: dataType,
        ignore_errors: ignoreErrors,
      };
      const outputColumn = {
        name: to,
        type: dataType,
        nullable: true,
        constraints: {},
      };
      if (dataType === 'decimal') {
        const precision = document.getElementById(`precision-${index}`).value;

        if (precision !== 'auto') {
          expression.precision = precision;
          outputColumn.constraints = { precision: parseInt(precision, 10) };
        }
      }
      if (columnIdInput) {
        outputColumn.id = columnIdInput.value;
      }
      data.settings.expressions.push(expression);
      data.columns.output.push(outputColumn);
    }

    try {
      const overview = await validate('formula', data);
      if (overview.error) {
        throw new Error(overview.error);
      } else {
        const inputColumns = await getJQInput({
          expressions: data.settings.expressions,
          columns,
        });
        if (inputColumns.error) {
          throw new Error(inputColumns.error);
        } else {
          data.columns.input = inputColumns;
        }
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

(0,dist/* default */.ZP)({ })
  .then(formula);


/***/ }),

/***/ 525:
/***/ (() => {

/* (ignored) */

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
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
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
/******/ 			2: 0
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
/******/ 		var chunkLoadingGlobal = self["webpackChunkconnect_transformations"] = self["webpackChunkconnect_transformations"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, [216], () => (__webpack_require__(506)))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;