'use strict';

import utils from './Utils';

/*-----------------------------------------------
|  Flex slider
-----------------------------------------------*/

utils.$document.ready(() => {
  const masks = $('[data-masking]');

  if(masks.length){
    masks.each((item, value) => {    
      const $this = $(value);
      const options = $this.data('masking');      
      $this.mask(options.mask, options.config ? options.config : '');
    });
  }

});