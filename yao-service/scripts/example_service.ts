import { Process, Exception } from '@yao/runtime';
import { getDataById, newData, saveDataByUUID, dataSearch } from '@scripts/service/model';
import { getNestedData } from '@scripts/service/nested_query';
import { getUserSession } from '@scripts/service/user';
import { RSuccess, RError } from '@scripts/return';
import { ModelProxy } from '@scripts/utils/proxy';

/**
 * 演示：业务服务层模式 (Drugstore Pattern)
 * 适用于大多数业务场景，如 CRUD、审核、状态流转
 */
export function businessServiceDemo(uuid: string, payload: any) {
    const user = getUserSession();

    // 1. 获取主记录 (含关联)
    const record = getDataById('medical.checkup', uuid, ['id', 'status', 'patient_id']);
    if (!record) return RError('记录不存在');

    // 2. 权限校验
    if (record.doctor_id !== user.user_id) {
        return RError('只能操作自己的记录');
    }

    // 3. 执行更新
    try {
        saveDataByUUID('medical.checkup', uuid, payload);
        return RSuccess(null, '更新成功');
    } catch (e) {
        return RError(e.message);
    }
}

/**
 * 演示：复杂嵌套查询层
 */
export function nestedQueryDemo(id: number) {
    const data = getNestedData('consult', id, {
        relations: ['doctor.hospital', 'patient', 'prescriptions.items.drug']
    });
    return RSuccess(data);
}

/**
 * 演示：代理层模式 (ModelProxy)
 * 适用于需要更偏向面向对象或链式操作的场景
 */
export function proxyDemo(keyword: string) {
    const userProxy = new ModelProxy('user');
    const query = {
        wheres: [{ column: 'name', op: 'like', value: `%${keyword}%` }],
        limit: 10
    };
    const list = userProxy.Get(query);
    return RSuccess(list);
}

/**
 * 演示：搜索模式 (dataSearch)
 */
export function searchDemo(page: number, perPage: number, querys: any) {
    const result = dataSearch('patient', page, perPage, querys, {}, {});
    return RSuccess(result);
}
