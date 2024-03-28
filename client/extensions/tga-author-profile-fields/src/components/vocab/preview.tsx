import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {IVocabularyFieldArrayValue, IVocabularyFieldConfig} from './interfaces';
import {SimpleList, SimpleListItem, Label} from 'superdesk-ui-framework/react';

type IProps = IPreviewComponentProps<IVocabularyFieldArrayValue, IVocabularyFieldConfig>;

export class VocabularyPreview extends React.PureComponent<IProps> {
    render() {
        return this.props.value == null || this.props.value.length === 0 ? null : (
            <div className="form__row form__row--small-padding">
                {!Array.isArray(this.props.value) ? (
                    <p className="sd-text__normal">
                        {this.props.value.name}
                    </p>
                ) : (
                    <SimpleList>
                        {this.props.value.map((value) => (
                            <SimpleListItem>
                                {value.qcode == null ? null : (
                                    <Label
                                        text={value.qcode}
                                        style="translucent"
                                    />
                                )}
                                <p className="sd-text__normal sd-whitespace--normal">
                                    {value.name}
                                </p>

                            </SimpleListItem>
                        ))}
                    </SimpleList>
                )}
            </div>
        );
    }
}
