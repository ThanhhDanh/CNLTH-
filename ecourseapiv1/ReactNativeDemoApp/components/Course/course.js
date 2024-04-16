import { View, Text, ActivityIndicator, ScrollView, Image } from "react-native";
import { List } from "react-native-paper";
import MyStyle from "../../Styles/MyStyle";

const Course =()=>{

    const [categories, setCategories] = React.useState(null);
    const[courses, setCourses] = React.useState([]);
    const [loading, setLoading] = React.useState(false)

    
    const loadCates = async ()=>{
        try{
            let res = await APIs.get(endponits['categories']);
            setCategories(res.data);
        }catch(ex){
            console.error(ex)
        }
    }


    const loadCourses = async ()=>{
        try{
            setLoading(true)
            let res = await APIs.get(endponits['courses']);
            setCourses(res.data.results);
        }catch(ex){
            console.error(ex)
        }
    }


    React.useEffect(()=>{
        loadCates();
    },[])

    React.useEffect(()=>{
        loadCourses();
    },[])



    return(
        <View style  = {MyStyle.container}>
            <Text style={MyStyle.subject}>Danh mục khóa học</Text>
            <View style={MyStyle.row}>
                {categories===null?<ActivityIndicator/>:<>
                    {categories.map(c=><Chip key={c.id} icon="shape">{c.name}</Chip>)}
                </>}
            </View>


            <ScrollView>
                {courses.map(c => <List.Item key={c.id} title={c.subject} description={c.created_date} 
                    left={() => <Image style={MyStyle.avatar} source={{uri: c.Image}}/>}/>)}
                {loading && <ActivityIndicator/>}
            </ScrollView>

        </View>
    )
}

export default Course