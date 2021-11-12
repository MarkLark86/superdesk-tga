import * as React from 'react';

import {IUser} from 'superdesk-api';
import {IEditorProps, IUserSignOff} from '../interfaces';
import {superdesk} from '../superdesk';

import {ButtonGroup, Button, Input, Checkbox} from 'superdesk-ui-framework/react';
import {hasUserSignedOff} from '../utils';

interface IProps {
    closeModal(): void
}

interface IState {
    signOff: IUserSignOff;
    isValid: boolean;
}

export function getUserSignOffModal(fieldProps: IEditorProps, currentUser: IUser) {
    return class UserSignOffModal extends React.Component<IProps, IState> {
        firstGroupRef: React.RefObject<HTMLDivElement>;

        constructor(props: IProps) {
            super(props);

            this.saveSignOff = this.saveSignOff.bind(this);
            this.firstGroupRef = React.createRef();

            const signOff: IUserSignOff = {
                user_id: fieldProps.value?.user_id || currentUser._id, // Should be populated by the current user
                funding_source: fieldProps.value?.funding_source,
                affiliation: fieldProps.value?.affiliation,
                consent_publish: fieldProps.value?.consent_publish ?? false,
                consent_disclosure: fieldProps.value?.consent_disclosure ?? false,
            };

            this.state = {
                signOff: signOff,
                isValid: hasUserSignedOff(signOff),
            };
        }

        componentDidMount() {
            this.firstGroupRef.current?.querySelector('input')?.focus();
        }

        saveSignOff() {
            const {dateToServerString} = superdesk.utilities;

            fieldProps.setValue({
                ...this.state.signOff,
                sign_date: dateToServerString(new Date()),
            })
            this.props.closeModal();
        }

        updateField<T extends keyof IUserSignOff>(field: T, value: IUserSignOff[T]) {
            this.setState((prevState) => {
                const newSignOff: IUserSignOff = {
                    ...prevState.signOff,
                    [field]: value,
                };

                return {
                    signOff: newSignOff,
                    isValid: hasUserSignedOff(newSignOff),
                };
            });
        }

        render() {
            const {gettext} = superdesk.localization;
            const {Modal, ModalHeader, ModalBody, ModalFooter} = superdesk.components;

            const isSameUser = this.state.signOff.user_id === currentUser._id;
            const disabled = fieldProps.readOnly || !isSameUser;
            const showSave = !(disabled || !isSameUser);

            return (
                <Modal size="large">
                    <ModalHeader onClose={this.props.closeModal}>
                        {gettext('Sign Off')}
                    </ModalHeader>
                    <ModalBody>
                        <div
                            className="form__group"
                            ref={this.firstGroupRef}
                        >
                            <div className="form__row">
                                <div className="form-label form-label--block">
                                    {gettext('Funding Source')}
                                </div>
                                <p className="sd-margin--0">
                                    What is the funding source for the research undertaken by you and
                                    being referred to in your contribution?<br/>
                                    If no research or not your research then state N/A.
                                </p>
                                <Input
                                    value={this.state.signOff.funding_source ?? ''}
                                    disabled={disabled}
                                    onChange={(value) => {
                                        this.updateField('funding_source', value);
                                    }}
                                />
                            </div>
                        </div>
                        <div className="form__group">
                            <div className="form__row">
                                <div className="form-label form-label--block">
                                    {gettext('Affiliation')}
                                </div>
                                <span>
                                    Do you have any financial, personal or political affiliation or
                                    other that may be perceived as a conflict in connection with
                                    your contribution?
                                </span>
                                <Input
                                    value={this.state.signOff.affiliation ?? ''}
                                    disabled={disabled}
                                    onChange={(value) => {
                                        this.updateField('affiliation', value);
                                    }}
                                />
                            </div>
                        </div>

                        <div className="form__group">
                            <div className="form__row">
                                <p className="sd-margin--0">
                                    We collect the above information in order to enable 360info to
                                    adhere to its charter by being transparent about funding and
                                    affiliations.
                                </p>
                            </div>
                        </div>
                        <div className="form__group">
                            <div className="form__row">
                                <div className="form-label form-label--block">
                                    {gettext('Consent')}
                                </div>
                                <Checkbox
                                    checked={this.state.signOff.consent_publish}
                                    disabled={disabled}
                                    label={{
                                        text: 'I consent to the personal information that I provide' +
                                            ' for 360info being used for the purposes of publishing' +
                                            ' my contribution.'
                                    }}
                                    onChange={(value) => {
                                        this.updateField('consent_publish', value);
                                    }}
                                />
                            </div>
                        </div>
                        <div className="form__group">
                            <div className="form__row">
                                <Checkbox
                                    checked={this.state.signOff.consent_disclosure}
                                    disabled={disabled}
                                    label={{
                                        text: 'I consent to the personal information that I provide ' +
                                            'for 360info being disclosed to the public on my ' +
                                            'published contribution.'
                                    }}
                                    onChange={(value) => {
                                        this.updateField('consent_disclosure', value);
                                    }}
                                />
                            </div>
                        </div>
                        <div className="form__group">
                            <div className="form__row">
                                <p className="sd-margin--0">
                                    360info values the privacy of every individual’s personal information
                                    and is committed to the protection of that information from
                                    unauthorised use and disclosure except where permitted by law.
                                    For more information about Data Protection and Privacy at Monash
                                    University please see our <a
                                    href="https://www.monash.edu/__data/assets/pdf_file/0003/790086/Privacy.pdf"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Data Protection and Privacy Procedure
                                </a>.
                                    If you have any questions about how 360info is collecting and
                                    handling your personal information, please contact our Data
                                    Protection and Privacy Office at <a
                                    href="mailto:dataprotectionofficer@monash.edu"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    dataprotectionofficer@monash.edu
                                </a>.
                                </p>
                            </div>
                        </div>
                    </ModalBody>
                    <ModalFooter>
                        <div className="sd-d-flex">
                            <ButtonGroup align="right">
                                <Button
                                    text={showSave ? gettext('Cancel') : gettext('Close')}
                                    onClick={this.props.closeModal}
                                />
                                {!showSave ? null : (
                                    <Button
                                        type="primary"
                                        text={fieldProps.value?.user_id == null ?
                                            gettext('Sign') :
                                            gettext('Update')
                                        }
                                        onClick={this.saveSignOff}
                                        disabled={!this.state.isValid}
                                    />
                                )}
                            </ButtonGroup>
                        </div>
                    </ModalFooter>
                </Modal>
            );
        }
    }
}
