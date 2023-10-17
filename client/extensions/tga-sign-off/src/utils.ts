import {IArticle, IUser} from 'superdesk-api';
import {IPublishSignOff} from './interfaces';
import {superdesk} from './superdesk';

export function hasUserSignedOff(item: IArticle): boolean {
    const publishSignOff: IPublishSignOff | undefined = item.extra?.publish_sign_off;

    if (publishSignOff == null || (publishSignOff?.sign_offs ?? []).length === 0) {
        return false;
    }

    const authorIds = getListAuthorIds(item);
    const signOffIds = publishSignOff.sign_offs.map((signOff) => signOff.user_id);

    if (signOffIds.length > 0) {
        // Make sure that all Author IDs have been signed off
        for (let i = 0; i < authorIds.length; i++) {
            if (!signOffIds.includes(authorIds[i])) {
                return false;
            }
        }

        for (let i = 0; i < publishSignOff.sign_offs.length; i++) {
            const signOff = publishSignOff.sign_offs[i];

            if (signOff.consent_publish === false || signOff.consent_disclosure === false) {
                return false;
            } else if (signOff.funding_source.trim().length === 0 || signOff.affiliation.trim().length === 0) {
                return false;
            }
        }

        return true;
    }

    return false;
}

export function getListAuthorIds(item: IArticle): Array<IUser['_id']> {
    // @ts-ignore
    return (item.authors ?? [])
        .map((author) => author.parent)
        .filter((authorId) => authorId != null);
}

export function loadUsersFromPublishSignOff(item: IArticle): Promise<{[userId: string]: IUser}> {
    const publishSignOff: IPublishSignOff | undefined = item.extra?.publish_sign_off;
    const userIds = getListAuthorIds(item).concat(
        (publishSignOff?.sign_offs ?? []).map((signOff) => signOff.user_id)
    ).concat(
        (publishSignOff?.pending_reviews ?? []).map((review) => review.user_id)
    );

    if (userIds.length === 0) {
        return Promise.resolve({});
    }

    return superdesk.entities.users.getUsersByIds(userIds).then((userArray) => {
        return userArray.reduce<{[userId: string]: IUser}>((users, user) => {
            users[user._id] = user;

            return users;
        }, {});
    });
}

interface ISignOffUserDetails {
    publishSignOff?: IPublishSignOff;
    signOffIds: Array<IUser['_id']>;
    unsentAuthorIds: Array<IUser['_id']>;
    pendingReviews: IPublishSignOff['pending_reviews'];
    requestUser?: IUser;
}

export function getSignOffDetails(item: IArticle, users: {[userId: string]: IUser}): ISignOffUserDetails {
    const publishSignOff: IPublishSignOff | undefined = item.extra?.publish_sign_off;
    const signOffIds: Array<IUser['_id']> = (
        (publishSignOff?.sign_offs ?? []).map((signOff) => signOff.user_id)
    ).concat(
        (publishSignOff?.pending_reviews ?? []).map((pendingReview) => pendingReview.user_id)
    );
    const unsentAuthorIds = getListAuthorIds(item)
        .filter((authorId) => !signOffIds.includes(authorId));
    const pendingReviews = (publishSignOff?.pending_reviews ?? []);
    const requestUser = publishSignOff?.requester_id == null ?
        undefined :
        users[publishSignOff.requester_id]

    return {
        publishSignOff,
        signOffIds,
        unsentAuthorIds,
        pendingReviews,
        requestUser,
    };
}
