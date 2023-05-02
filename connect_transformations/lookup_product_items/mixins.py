# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.constants import PRODUCT_ITEM_LOOKUP
from connect_transformations.lookup_product_items.utils import (
    extract_settings,
    generate_transformation_response,
    retrieve_product,
    retrieve_product_item,
    validate_lookup_product_item,
)
from connect_transformations.utils import is_input_column_nullable


class LookupProductItemsTransformationMixin:
    @transformation(
        name='Lookup CloudBlue Product Item Data',
        description=(
            'This transformation function allows to search for the corresponding CloudBlue '
            'Product Item data.'
        ),
        edit_dialog_ui='/static/transformations/lookup_product_item.html',
    )
    async def lookup_product_items(
            self,
            row: dict,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        product_id, from_column, leave_empty = extract_settings(trfn_settings, row)

        if self._should_skip_row(trfn_settings, from_column, row):
            return RowTransformationResponse.skip()

        try:
            product = await retrieve_product(
                self.installation_client,
                self._cache,
                self._cache_lock,
                product_id,
                leave_empty,
            )
            if not product and leave_empty:
                return RowTransformationResponse.skip()

            product_item = await self._get_product_item(
                trfn_settings, product, row[from_column], leave_empty,
            )
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        return generate_transformation_response(trfn_settings, product_item)

    def _should_skip_row(self, trfn_settings, from_column, row):
        return (
            is_input_column_nullable(
                self.transformation_request['transformation']['columns']['input'],
                from_column,
            )
            and not row[trfn_settings['from']]
        )

    async def _get_product_item(self, trfn_settings, product, value, leave_empty):
        return await retrieve_product_item(
            self.installation_client,
            self._cache,
            self._cache_lock,
            product,
            trfn_settings['lookup_type'],
            value,
            leave_empty,
        )


class LookupProductItemsWebAppMixin:
    @router.post(
        '/validate/lookup_product_item',
        summary='Validate lookup product settings',
    )
    def validate_lookup_product_item_settings(
            self,
            data: dict,
    ):
        return validate_lookup_product_item(data)

    @router.get(
        '/lookup_product_item/criteria',
        summary='Return the product criteria options',
    )
    def get_product_item_criteria(
            self,
    ):
        return PRODUCT_ITEM_LOOKUP
