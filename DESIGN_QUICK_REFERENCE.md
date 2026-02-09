# 🎨 Quick Reference - UI/UX Design

## 📱 MOBILE APP - CLIENT

### Ключевые экраны (Priority Order)
```
1. 🏠 Home/Catalog         - Main screen
2. 🚗 Car Detail           - Most important
3. 📝 Create Application   - Conversion point
4. 📋 My Applications      - User engagement
5. 🔍 Search/Filters       - Discovery
6. 👤 Profile              - User management
```

### Главные фичи
```
✨ Только НОВЫЕ автомобили из США
💰 Прозрачная цена (базовая + наценка = финальная)
⭐ Избранное
📍 Отслеживание статуса заявки в реальном времени
📄 Просмотр документов
💬 Связь с менеджером
```

### Навигация
```
Bottom Tab Bar:
┌────────────────────────────┐
│  🏠      📋      ⭐      👤  │
│ Home  Заявки  Wish   Profile│
└────────────────────────────┘
```

---

## 💻 WEB DASHBOARD - STAFF

### Структура
```
┌─────────────────────────────────┐
│ Logo   🔍 Search   👤 Profile   │ ← Top Bar
├─────┬───────────────────────────┤
│ Nav │   Content Area            │
│ Bar │                           │
└─────┴───────────────────────────┘
```

### Sidebar Navigation (by Role)

**All Staff:**
```
📊 Dashboard
📋 Applications
🚗 Catalog
```

**Supervisor+:**
```
+ 🚫 Blacklist
+ 👥 Users (view)
```

**Manager+:**
```
+ 💳 Payments
+ 📄 Documents
```

**Admin+:**
```
+ ⚙️ Settings
+ 📜 Audit Logs
+ 👥 Users (manage)
```

**Owner:**
```
+ 👑 Role Management
+ 🔧 Business Config
```

---

## 🎯 User Journey Maps

### CLIENT: Покупка автомобиля
```
Открыть App
    ↓
Просмотр каталога (фото, цены)
    ↓
Фильтры (марка, год, цена)
    ↓
Выбор авто → Детали
    ↓
"Оставить заявку" 💚
    ↓
Заполнение (автозаполнение данных)
    ↓
Подтверждение ✅
    ↓
Ожидание звонка 📞
    ↓
Отслеживание статуса 📊
    ↓
Оплата (загрузка чека) 💳
    ↓
Получение документов 📄
    ↓
Доставка автомобиля 🚗✨
```

### OPERATOR: Обработка заявки
```
Login → Dashboard
    ↓
Видит новые заявки (уведомление 🔔)
    ↓
Открывает заявку #1234
    ↓
Видит: Клиента, Авто, Контакты
    ↓
Звонит клиенту ☎️
    ↓
Обновляет:
  - Контакт-статус: "Связались"
  - Чеклист: ✅ Подтвердил интерес
  - Комментарий: "Клиент готов"
    ↓
Меняет статус: NEW → CONFIRMED 🟢
    ↓
Передает Manager
```

### MANAGER: Завершение сделки
```
Dashboard → Payments
    ↓
Видит заявку CONFIRMED
    ↓
Создает счет (Invoice) 🧾
    ↓
Клиент загружает чек
    ↓
Проверяет чек ✅
    ↓
Подтверждает платеж 💰
    ↓
Статус → PAID
    ↓
Загружает договор 📄
    ↓
Загружает видео-подпись 📹
    ↓
Статус → CONTRACT_SIGNED ✅
    ↓
Организует доставку 🚚
```

---

## 🎨 Visual Style Guide

### Colors Quick Reference
```
Primary Actions:   #2563EB (Blue)
Success:           #10B981 (Green)
Warning:           #F59E0B (Amber)
Error:             #EF4444 (Red)

Status Badges:
🟡 New             #FCD34D
🔵 Processing      #60A5FA
🟢 Success         #34D399
🔴 Cancelled       #F87171
```

### Typography
```
Mobile:
H1: 28px Bold
H2: 22px Bold
Body: 16px
Small: 12px

Web:
H1: 32px Bold
H2: 24px Bold
Body: 16px
Small: 14px
```

### Components Spacing
```
Extra Small:   4px
Small:         8px
Medium:        16px
Large:         24px
Extra Large:   32px
```

---

## 🚀 Priority Features for MVP

### Mobile (Phase 1)
```
✅ Auth (OTP)
✅ Catalog browse
✅ Car details
✅ Create application
✅ Track application status
✅ View documents
✅ Profile management
```

### Web (Phase 1)
```
✅ Auth (password)
✅ Operator dashboard
✅ Applications management
✅ Contact status update
✅ CRM checklist
✅ Manager payment confirm
✅ Document upload
```

### Phase 2
```
📱 Push notifications
📱 Favorites/Wishlist
💻 Advanced analytics
💻 Bulk operations
💻 Real-time updates (WebSocket)
💻 Dark mode
```

---

## 📊 Status Flow Visualization

```
CLIENT VIEW (Mobile):
🟡 Новая заявка
    ↓
🔵 Обработка (оператор звонит)
    ↓
🟢 Подтверждено (готов покупать)
    ↓
💰 Ожидание оплаты
    ↓
✅ Оплачено
    ↓
📝 Договор подписан
    ↓
📦 Грузовая отправка
    ↓
🚢 В пути
    ↓
🎉 Доставлено
    ↓
✨ Завершено
```

```
STAFF VIEW (Web):
NEW
    ↓ [Operator]
IN_CALLCENTER
    ↓ [Operator]
CONFIRMED
    ↓ [Manager]
WAITING_PAYMENT
    ↓ [Manager - после подтверждения]
PAID
    ↓ [Manager]
CONTRACT_SIGNED
    ↓ [Manager]
CARGO_BOOKED
    ↓ [Manager]
IN_TRANSIT
    ↓ [Manager]
DELIVERED
    ↓ [Manager]
COMPLETED ✅

Или:
ANY STATUS → CANCELLED ❌ (с причиной)
```

---

## 🎯 Key Metrics to Display

### Client Dashboard:
```
- Активных заявок
- Сумма всех покупок
- Следующий шаг (что делать)
```

### Operator Dashboard:
```
- Новых заявок сегодня
- Моих активных заявок
- Требуют звонка
- Callback список
```

### Manager Dashboard:
```
- Ожидают оплаты
- Неподтвержденных платежей
- Доход за месяц
- Активных сделок
```

### Admin Dashboard:
```
- Всего заявок
- Conversion rate
- Средний чек  
- Revenue этот месяц
- Team performance
```

---

## 💡 UX Tips

### Mobile:
```
✨ Большие фото машин (swipeable)
✨ Крупные кнопки (48px height)
✨ Минимум текста
✨ Плавные анимации
✨ Pull-to-refresh
✨ Empty states с иллюстрациями
```

### Web:
```
✨ Keyboard shortcuts (Ctrl+K для поиска)
✨ Bulk actions (checkbox for multi-select)
✨ Quick filters (pills above table)
✨ Export buttons
✨ Real-time badges (new applications)
✨ Inline editing where possible
```

---

## 🔔 Notifications

### Mobile Push:
```
📱 "Ваша заявка #1234 подтверждена!"
📱 "Требуется загрузить чек об оплате"
📱 "Ваш автомобиль в пути! 🚢"
📱 "Новое сообщение от менеджера"
```

### Web Toast:
```
💻 "Статус заявки #1234 обновлен"
💻 "Новая заявка от +998 90 123-4567"
💻 "Платеж подтвержден"
💻 "Документ успешно загружен"
```

---

## 🎨 Example Screens Priority

### Must Design First:
1. **Mobile: Car Catalog** - главный экран
2. **Mobile: Car Detail** - конверсия
3. **Mobile: Create Application** - форма заявки
4. **Web: Applications List** - основная работа
5. **Web: Application Detail** - детали и действия

### Design Next:
6. Mobile: Application Tracking
7. Web: Payments Manager
8. Web: Operator Dashboard
9. Mobile: Profile
10. Web: Documents Upload

---

## ✅ Checklist for Designers

### Mobile App:
- [ ] Onboarding flow (3-4 screens)
- [ ] Auth (OTP entry)
- [ ] Home/Catalog (grid + filters)
- [ ] Car Detail (photos + specs + CTA)
- [ ] Application Form
- [ ] My Applications List
- [ ] Application Detail (timeline)
- [ ] Profile
- [ ] Empty States
- [ ] Loading States
- [ ] Error States

### Web Dashboard:
- [ ] Login
- [ ] Sidebar Navigation
- [ ] Operator Dashboard
- [ ] Applications Table
- [ ] Application Detail (CRM)
- [ ] Payments Manager
- [ ] Documents Upload
- [ ] Users Management (Admin)
- [ ] Blacklist (Supervisor)
- [ ] Audit Logs (Admin)

---

**Remember:**
- 📱 Mobile = Visual & Simple
- 💻 Web = Data & Efficient
- 🎨 Consistency across platforms
- ⚡ Performance first
- 🔐 Security visible (locks, confirmations)

---

**Version:** 1.0  
**Date:** 01.02.2026
