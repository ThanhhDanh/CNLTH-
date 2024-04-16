import axios from "axiox"

const BASE_URL= 'https://thanhduong.pythonanywhere.com/'

export const endponits = {
    "categories":"/categories/"
}

export default axios.create({
    baseURL: BASE_URL
})