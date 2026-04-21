import { showUserInfo } from '../ui/render.js'
import { connectToUserChannel } from './socket.js'

export async function checkAuth() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();
        
        if (response.status !== 200) {
            window.location.href = '/login';
            return;
        }
        
        // showUserInfo(data.data.user);
        connectToUserChannel();
    } catch (error) {
        console.error(error);
        window.location.href = '/login';
    }
}