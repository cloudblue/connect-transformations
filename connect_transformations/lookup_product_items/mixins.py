# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

from connect.client import ClientError
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.lookup_product_items.exceptions import ProductLookupError
from connect_transformations.lookup_product_items.models import Configuration
from connect_transformations.lookup_product_items.utils import (
    PRODUCT_ITEM_LOOKUP,
    extract_settings,
    generate_transformation_response,
    validate_lookup_product_item,
)
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable


class LookupProductItemsTransformationMixin:
    @transformation(
        name='Lookup CloudBlue product item',
        description=(
            'This transformation function allows you to get the'
            ' CloudBlue product item data by the product item ID or MPN.'
        ),
        edit_dialog_ui='/static/transformations/lookup_product_item.html',
    )
    async def lookup_product_items(
            self,
            row: Dict,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        product_id, from_column, leave_empty = extract_settings(trfn_settings, row)

        if self._should_skip_row(trfn_settings, from_column, row):
            return RowTransformationResponse.skip()

        try:
            product = await self.retrieve_product(product_id, leave_empty)
            if not product and leave_empty:
                return RowTransformationResponse.skip()

            product_item = await self.retrieve_product_item(
                product, trfn_settings['lookup_type'], row[from_column].strip(), leave_empty,
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

    async def retrieve_product(self, product_id, leave_empty):
        try:
            return self.cache_get(product_id)
        except KeyError:
            pass
        try:
            product = await self.installation_client.products[product_id].get()
            await self.acache_put(product_id, product)
            return product
        except Exception as e:
            if leave_empty:
                return
            raise ProductLookupError(f'Error retrieving the product {product_id}: {str(e)}')

    async def get_product_item_by_filter(self, product, lookup_value):
        filter_expression = f"eq(mpn,{lookup_value})"
        count = await self.installation_client.products[product['id']].items.filter(
            filter_expression,
        ).count()
        if count == 0:
            return None
        elif count > 1:
            raise ProductLookupError(f'Multiple results found for the filter: {lookup_value}')

        return await self.installation_client.products[product['id']].items.filter(
            filter_expression,
        ).first()

    async def retrieve_product_item(
            self, product, lookup_type, lookup_value, leave_empty,
    ):
        cache_key = f'{product["id"]}-{lookup_type}-{lookup_value}'
        try:
            return self.cache_get(cache_key)
        except KeyError:
            pass

        if lookup_type not in PRODUCT_ITEM_LOOKUP:
            raise ProductLookupError('Unknown lookup type')

        product_item = None
        if lookup_type == 'id':
            try:
                product_item = await self.installation_client.products[
                    product['id']
                ].items[lookup_value].get()
            except ClientError:
                pass
        else:
            product_item = await self.get_product_item_by_filter(product, lookup_value)

        if product_item is None:
            if leave_empty:
                return
            raise ProductLookupError('Product not found')

        product_item['product'] = product
        await self.acache_put(cache_key, product_item)
        return product_item


class LookupProductItemsWebAppMixin:
    @router.post(
        '/lookup_product_item/validate',
        summary='Validate lookup product settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_lookup_product_item_settings(
            self,
            data: Configuration,
    ):
        return validate_lookup_product_item(data)
