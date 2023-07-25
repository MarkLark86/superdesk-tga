import * as React from 'react';

import {ILiveResourcesProps, IRestApiResponse, IVocabulary, IVocabularyItem, IEditorComponentProps} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {IVocabularyFieldConfig} from './interfaces';

import {Select, Option, MultiSelect, Label} from 'superdesk-ui-framework/react';

type IVocabularyFieldValue = IVocabularyItem | Array<IVocabularyItem> | null | undefined;
type IVocabularyFieldProps = IEditorComponentProps<IVocabularyFieldValue, IVocabularyFieldConfig>

function getValueAsArray(value: IVocabularyFieldValue): Array<IVocabularyItem> {
    if (value == null) {
        return [];
    } else if (!Array.isArray(value)) {
        return [value];
    }

    return value;
}

function getValueAsDictionary(value: IVocabularyFieldValue): IVocabularyItem | null {
    if (value == null) {
        return null;
    } else if (Array.isArray(value)) {
        return value[0];
    }

    return value;
}


export class VocabularyField extends React.PureComponent<IVocabularyFieldProps> {
    render() {
        if (this.props.config?.vocabulary_name == null) {
            return null;
        }

        const {WithLiveResources} = superdesk.components;
        const resources: ILiveResourcesProps['resources'] = [
            {resource: 'vocabularies', ids: [this.props.config.vocabulary_name]}
        ];

        return (
            <WithLiveResources resources={resources}>
                {(resourcesResponse) => {
                    const vocab = resourcesResponse[0] as IRestApiResponse<IVocabulary>;
                    const isMultiSelect = vocab._items[0].selection_type === 'multi selection';
                    const items = vocab._items[0].items;

                    return isMultiSelect ? (
                        <MultiSelect
                            value={getValueAsArray(this.props.value)}
                            options={items}
                            placeholder={'Select an item'}
                            optionLabel={(item) => item?.name || ''}
                            onChange={(newValues) => {
                                this.props.setValue(newValues);
                            }}
                            filter={true}
                            labelHidden={true}
                            label={'CV Items'}
                            inlineLabel={true}
                            itemTemplate={(item) => (
                                <div
                                    className="sd-container sd-container--gap-medium"
                                    style={{maxWidth: '600px'}} // Define max-width, so SDGs will fit in screen
                                >
                                    <Label
                                        text={item.qcode}
                                        style="translucent"
                                    />
                                    <span className="sd-text__normal sd-whitespace--normal">
                                        {item.name}
                                    </span>
                                </div>
                            )}
                        />
                    ) : (
                        <Select
                            onChange={(qcode) => {
                                this.props.setValue(items.find((item) => item.qcode === qcode));
                            }}
                            value={getValueAsDictionary(this.props.value)?.qcode}
                            inlineLabel={true}
                            label={'CV Item'}
                            labelHidden={true}
                            disabled={this.props.readOnly}
                        >
                            <Option />
                            {items.map((item) => (
                                <Option key={item.qcode} value={item.qcode}>{item.name}</Option>
                            ))}
                        </Select>
                    );
                }}
            </WithLiveResources>
        );
    }
}
