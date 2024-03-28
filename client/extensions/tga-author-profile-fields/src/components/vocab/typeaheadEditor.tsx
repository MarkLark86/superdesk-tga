import * as React from 'react';

import {ILiveResourcesProps, IRestApiResponse, IVocabulary, IVocabularyItem, IEditorComponentProps} from 'superdesk-api';
import {superdesk} from '../../superdesk';

import {Autocomplete} from 'superdesk-ui-framework/react';
import {IVocabularyFieldConfig, IVocabularyFieldValue} from "./interfaces";


type IVocabularyFieldProps = IEditorComponentProps<IVocabularyFieldValue, IVocabularyFieldConfig, never>;
const NEW_ITEM_PREFIX = '_new:';

export class VocabularyTypeaheadField extends React.PureComponent<IVocabularyFieldProps> {
    render() {
        const {gettext} = superdesk.localization;
        const {WithLiveResources} = superdesk.components;
        const resources: ILiveResourcesProps['resources'] = [
            {resource: 'vocabularies', ids: [this.props.config?.vocabulary_name]}
        ];

        return (
            <WithLiveResources resources={resources}>
                {(resourcesResponse) => {
                    const vocab = resourcesResponse[0] as IRestApiResponse<IVocabulary>;
                    const items = vocab._items[0].items;

                    const searchItems = (searchString: string, callback: (result: Array<IVocabularyItem>) => void) => {
                        const filteredItems = items.filter((item) => item.name?.toLowerCase().includes(searchString.toLowerCase()));

                        if (this.props.config.allow_freetext && filteredItems.find((item) => item.name?.toLowerCase() === searchString.toLowerCase()) == null) {
                            filteredItems.unshift({
                                qcode: `${NEW_ITEM_PREFIX}${searchString}`,
                                name: gettext('{{ item }} (added on save)', {item: searchString}),
                            });
                        }

                        callback(filteredItems);

                        return {cancel: () => {}};
                    }

                    if (
                        this.props.value?.qcode != null &&
                        items.find((item) => item.qcode?.toLowerCase() === this.props.value?.qcode)
                    ) {
                        // The current item is not in the CV, must be a new item to be added
                        items.push(this.props.value);
                    }

                    return (
                        <Autocomplete
                            value={this.props.value ?? undefined}
                            keyValue="name"
                            items={items}
                            search={searchItems}
                            minLength={0}
                            onChange={(val) => {
                                if (val.length === 0) {
                                    // Remove the selected item
                                    this.props.onChange(null);
                                }
                            }}
                            onSelect={(value: any) => {
                                const newItem = value as IVocabularyItem;

                                if (newItem.qcode?.startsWith(NEW_ITEM_PREFIX)) {
                                    newItem.name = newItem.qcode.replace(NEW_ITEM_PREFIX, '');
                                    newItem.qcode = newItem.name.replace(/ /g, '_');
                                }

                                this.props.onChange(newItem);
                            }}
                            disabled={this.props.readOnly}
                        />
                    );
                }}
            </WithLiveResources>
        );
    }
}
