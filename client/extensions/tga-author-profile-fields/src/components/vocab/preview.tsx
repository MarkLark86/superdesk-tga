import * as React from 'react';

import {IPreviewComponentProps, IVocabularyItem} from 'superdesk-api';
import {SimpleList, SimpleListItem, Label} from 'superdesk-ui-framework/react';

export class VocabularyPreview extends React.PureComponent<IPreviewComponentProps<IVocabularyItem | Array<IVocabularyItem>>> {
    render() {
        return (
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
