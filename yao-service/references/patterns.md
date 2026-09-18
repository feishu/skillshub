# Service Project Patterns

## 1. 业务脚本结构 (Standard Business Service)
位于 `scripts/service/*.ts`。

```typescript
import { getDataById, saveDataByUUID } from '@scripts/service/model';
import { getUserSession } from '@scripts/service/user';
import { RSuccess, RError } from '@scripts/return';

/**
 * 业务功能：执行订单审批
 * yao run scripts.service.order.approve <order_uuid>
 */
export function approve(orderUuid: string) {
  const user = getUserSession();
  const order = getDataById('order', orderUuid);
  
  if (!order) return RError('订单不存在');
  if (user.user_type !== 'STAFF') return RError('无权审批');

  try {
    saveDataByUUID('order', orderUuid, { 
      status: 'APPROVED', 
      approver_id: user.user_id 
    });
    return RSuccess(null, '审批成功');
  } catch(e) {
    return RError(e.message);
  }
}
```

## 2. 原子同步模式 (Atomic Sync)
用于简单的外部同步或低级数据修正。

```typescript
import { saveModelData } from '@scripts/utils/processor';

export function sync(data: any) {
  // saveModelData 自动处理 updateInputData (UUID, 类型转换等)
  return saveModelData('external_data_model', data, 'create');
}
```

## 3. 嵌套查询模式 (Deep Fetching)
```typescript
import { getNestedData } from '@scripts/service/nested_query';

export function getFullDetail(id: number) {
  return getNestedData('consult', id, {
    relations: ['doctor', 'patient.profiles', 'prescriptions.items']
  });
}
```

## 4. 模型定义 (Model DSL)
```json
{
  "name": "示例模型",
  "table": { "name": "t_example" },
  "columns": [
    { "name": "id", "type": "ID", "primary": true },
    { "name": "uuid", "type": "uuid", "index": true, "unique": true },
    { "name": "name", "type": "string", "length": 50, "index": true }
  ],
  "option": { "timestamps": true, "soft_deletes": true }
}
```
