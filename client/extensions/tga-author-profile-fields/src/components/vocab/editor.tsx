import * as React from 'react';

import {ILiveResourcesProps, IRestApiResponse, IVocabulary} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {IVocabularyFieldProps} from './interfaces';

import {Select, Option} from "superdesk-ui-framework/react";


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
                    const items = vocab._items[0].items;

                    return (
                        <Select
                            onChange={(qcode) => {
                                this.props.setValue(items.find((item) => item.qcode === qcode));
                            }}
                            value={this.props.value?.qcode}
                            inlineLabel={true}
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
