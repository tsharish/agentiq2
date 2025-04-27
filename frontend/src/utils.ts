export function getAccessToken() {
    let user = null
    let token = ''
    const userInStorage = localStorage.getItem('user')

    if (userInStorage) {
        user = JSON.parse(userInStorage)
    }

    if (user && user.access_token) {
        token = `Bearer ${user.access_token}`
    }

    return token
}
