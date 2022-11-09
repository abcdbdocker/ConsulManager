<template>
    <el-main>
        <el-tabs :tab-position="tabPosition" style="height: auto;width: 600px;">
            <el-tab-pane label="统一认证">
                <!-- 统一认证 -->
                <el-form :model="ruleForm"  status-icon :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm">
                    <el-form-item label="认证地址:" prop="ldap_url">
                        <el-input type="text" v-model="ruleForm.ldap_url" autocomplete="off"></el-input>
                    </el-form-item>

                    <el-form-item label="端口号:" prop="port">
                        <el-input type="text" v-model="ruleForm.port" autocomplete="off"></el-input>
                    </el-form-item>

                    <el-alert
                        class="alert"
                        title="示例:{'cn=cn,dc=dc,dc=dc'}"
                        type="info">
                    </el-alert>
                    <el-form-item label="认证规则:" prop="rule">
                        <el-input type="text" v-model="ruleForm.rule" autocomplete="off"></el-input>
                    </el-form-item>
                    
                    <el-form-item label="认证密码:" prop="password">
                        <el-input type="password" v-model="ruleForm.password" autocomplete="off"></el-input>
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
                        <el-button @click="resetForm('ruleForm')">重置</el-button>
                    </el-form-item>
                    </el-form>

            </el-tab-pane>
        </el-tabs>
    </el-main>
</template>
<script>

import { setldap } from '@/api/ldap'
import { number } from 'yargs';

export default {
    data(){
        var checkAge = (rule, value, callback) => {
            value = number(value)
            console.log(value)
            if (typeof(value) != number) {
                return callback(new Error('端口号必须为整数'));
            }
        }
        return{
            tabPosition:"left",
            ruleForm:{}, //存储ldap
            rules:{
                ldap_url: [
                    { validator: "xxx", trigger: 'blur' }
                ],
                port: [
                    { validator: "xxxx", trigger: 'blur' }
                ],
                rule: [
                    { validator: "xxx", trigger: 'blur' }
                ],
                password: [
                    { validator: "xxx", trigger: 'blur' }
                ],
            }, //校验规则
        }
    },
    
    methods:{
        submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            //使用箭头函数进行发送请求
            setldap(this.ruleForm).then(response =>{
                if (response.code == 200){
                    this.$message({
                    type: 'success',
                    message: response.message
                    })
                    return
                }
                this.$message({
                    type: 'error',
                    message: response.message
                    })
            })

          } else {

            console.log('error submit!!');

            return false;
          }
        });
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      }

    }
    
}


</script>


<style lang="scss">
.alert{
    width: 500px;
    margin-left:100px ;
    margin-bottom:2px ;
}
</style>