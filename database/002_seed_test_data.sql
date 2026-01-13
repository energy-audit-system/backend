-- Тестовые данные для Energy Audit System
-- Дата: 2026-01-13
-- Описание: Фейковые данные для разработки и тестирования

-- ============================================
-- ОЧИСТКА СУЩЕСТВУЮЩИХ ТЕСТОВЫХ ДАННЫХ
-- ============================================

-- Удаляем только тестовые данные (пользователей с @example.com)
-- Cascade удалит связанные записи
DELETE FROM auth.users WHERE email LIKE '%@example.com';

-- Сброс счетчиков ID для предсказуемых ID (опционально)
-- Раскомментируйте, если нужны предсказуемые ID начиная с 1
-- ALTER SEQUENCE auth.users_id_seq RESTART WITH 1;
-- ALTER SEQUENCE core.business_id_seq RESTART WITH 1;
-- ALTER SEQUENCE core.audit_orders_id_seq RESTART WITH 1;
-- ALTER SEQUENCE reports.reports_id_seq RESTART WITH 1;
-- ALTER SEQUENCE reports.files_id_seq RESTART WITH 1;
-- ALTER SEQUENCE logs.report_history_id_seq RESTART WITH 1;

-- ============================================
-- USERS - Пользователи системы
-- ============================================

-- Пароль для всех тестовых пользователей: "password123"
-- Hash сгенерирован через werkzeug.security.generate_password_hash

INSERT INTO auth.users (full_name, email, phone, password_hash, role, is_email_verified, email_verification_token) VALUES
-- Инженеры
('Иванов Иван Петрович', 'engineer1@example.com', '+7 (999) 111-22-33', 'scrypt:32768:8:1$0osS5t9h4At2vCjB$66d2fec06eb5ee3df5b40db6ea8b1de786cd158fc1105cd98ac6403428dfe7baa7d706c09bd11ddffd2c22e60f40261d3d7094209a0897671041472d06700a8e', 'engineer', true, NULL),
('Петрова Мария Александровна', 'engineer2@example.com', '+7 (999) 222-33-44', 'scrypt:32768:8:1$OMOopYYDWIsighh7$2df680bf20d5e47aaaf9d5228658dc0159521bd370e19501020006d63c08bd98a983c4d1982bc1ffb9dca91c25ce2a6b4d9f9bec8df06799a864277c12ad14a9', 'engineer', true, NULL),
('Сидоров Алексей Викторович', 'engineer3@example.com', '+7 (999) 333-44-55', 'scrypt:32768:8:1$6epQuhKe9pHKxEzW$13daf70c9dff958497a184815dfcefdeef6fb1516a3fb7ff115e82e3ca3071eebdfd8ce57fd6e1ffa46037b4cf3441b0afa1af2d90e7048dca15e6e3121a3992', 'engineer', true, NULL),

-- Клиенты
('Смирнов Дмитрий Олегович', 'client1@example.com', '+7 (999) 444-55-66', 'scrypt:32768:8:1$cFdKgwRhARnkx48Q$1ce1277922ff4467d0b8b15a17e1076d9cee805e9adc77a2845e7347a49099f0b5cf69e8077901ee6004c3d46391f711a80fecd6d596ed7550efc2ddcba4ed7b', 'client', true, NULL),
('Кузнецова Елена Сергеевна', 'client2@example.com', '+7 (999) 555-66-77', 'scrypt:32768:8:1$NqGuojfsiU3rQLs2$8871b1edd1e55e22006ba56fe2bd329970afaf03783baa6cf07ff3ab3f50740057ef66d6ae2a2b0edcd5bb98a04fdf3196b7f49522f0607208fbb118f5873858', 'client', true, NULL),
('Попов Андрей Николаевич', 'client3@example.com', '+7 (999) 666-77-88', 'scrypt:32768:8:1$eguM3Nm1DQjjjiKs$333e25aedf34e5308090a0143ff23f7d54558c4df3f6c801c433410221cbc7a10fc2d3527e025c4614d30b70676ef6de0af2b4261c7a819885f5b80498dc1c79', 'client', true, NULL),
('Васильева Ольга Ивановна', 'client4@example.com', '+7 (999) 777-88-99', 'scrypt:32768:8:1$wtiQt2OfRaW7SAvQ$cf882c9e0a05a83f0f5f3b13bde3134b6556a814bb378f9d4171c1a5af64ddb7c582227a8b845b2bde203e0072c986fd2522471e42619de54e1d96c832551a0d', 'client', true, NULL),

-- Администраторы
('Администратов Админ Админович', 'admin@example.com', '+7 (999) 000-00-00', 'scrypt:32768:8:1$tg3FcOXITs8uundj$2d6509f4160a829bc0226f3b86cbe5d5ba20c3d2df7acc8f345ac1e18fdf81aad59246f21f0b87b2c2a3f3a9343724e250ab984a35f8ebd18c28ed67338c9727', 'admin', true, NULL);

-- ============================================
-- BUSINESS - Предприятия клиентов
-- ============================================

-- Используем подзапросы для получения ID пользователей по email
INSERT INTO core.business (business_name, address, inn, owner_id) VALUES
('ООО "ЭнергоПром"', 'г. Москва, ул. Ленина, д. 10, оф. 5', '7707123456',
    (SELECT id FROM auth.users WHERE email = 'client1@example.com')),
('АО "ТеплоЭнерго"', 'г. Санкт-Петербург, Невский пр., д. 25', '7812234567',
    (SELECT id FROM auth.users WHERE email = 'client2@example.com')),
('ИП Попов А.Н.', 'г. Екатеринбург, ул. Мира, д. 15', '6658345678',
    (SELECT id FROM auth.users WHERE email = 'client3@example.com')),
('ООО "СветТорг"', 'г. Новосибирск, пр. Карла Маркса, д. 7', '5406456789',
    (SELECT id FROM auth.users WHERE email = 'client4@example.com')),
('ООО "ПромСтрой"', 'г. Казань, ул. Баумана, д. 30', '1655567890',
    (SELECT id FROM auth.users WHERE email = 'client1@example.com'));

-- ============================================
-- AUDIT_ORDERS - Заказы на энергоаудит
-- ============================================

INSERT INTO core.audit_orders (business_id, status, access_until, building_type, building_subtype, order_data) VALUES
-- Завершенные заказы
(1, 'paid', '2027-12-31', 'Производственное здание', 'Завод',
    '{"area": 5000, "floors": 3, "year_built": 1995, "heating_type": "Централизованное", "employees": 150, "working_hours": "24/7"}'::jsonb),

(2, 'ready', '2027-06-30', 'Офисное здание', 'Бизнес-центр',
    '{"area": 3500, "floors": 7, "year_built": 2005, "heating_type": "Автономное", "employees": 200, "working_hours": "8:00-18:00"}'::jsonb),

-- Заказы в процессе
(3, 'in_progress', '2026-12-31', 'Торговое здание', 'Магазин',
    '{"area": 800, "floors": 1, "year_built": 2010, "heating_type": "Централизованное", "employees": 25, "working_hours": "9:00-21:00"}'::jsonb),

(4, 'in_progress', '2027-03-31', 'Складское здание', 'Логистический центр',
    '{"area": 10000, "floors": 2, "year_built": 2015, "heating_type": "Автономное", "employees": 50, "working_hours": "6:00-22:00"}'::jsonb),

-- Ожидающие заказы
(5, 'pending', '2026-09-30', 'Производственное здание', 'Цех',
    '{"area": 2000, "floors": 1, "year_built": 1988, "heating_type": "Централизованное", "employees": 80, "working_hours": "8:00-17:00"}'::jsonb),

(1, 'pending', '2027-01-31', 'Административное здание', 'Офис',
    '{"area": 1200, "floors": 4, "year_built": 2000, "heating_type": "Автономное", "employees": 60, "working_hours": "9:00-18:00"}'::jsonb);

-- ============================================
-- REPORTS - Отчёты по энергоаудиту
-- ============================================

INSERT INTO reports.reports (audit_order_id, version, status, data, access_until) VALUES
-- Отчёт для первого заказа (финальный)
(1, 1, 'final',
    '{
        "executive_summary": "Проведен комплексный энергоаудит производственного здания площадью 5000 кв.м",
        "energy_consumption": {
            "electricity_kwh_year": 850000,
            "electricity_cost_rub": 4250000,
            "gas_m3_year": 120000,
            "gas_cost_rub": 840000,
            "water_m3_year": 15000,
            "water_cost_rub": 525000,
            "total_cost_rub": 5615000
        },
        "energy_efficiency_class": "D",
        "recommendations": [
            {
                "id": 1,
                "title": "Замена освещения на LED",
                "description": "Установка светодиодных светильников вместо люминесцентных",
                "investment_rub": 500000,
                "savings_kwh_year": 85000,
                "savings_rub_year": 425000,
                "payback_period_years": 1.2,
                "priority": "high"
            },
            {
                "id": 2,
                "title": "Установка частотных преобразователей",
                "description": "ЧП на насосное и вентиляционное оборудование",
                "investment_rub": 800000,
                "savings_kwh_year": 120000,
                "savings_rub_year": 600000,
                "payback_period_years": 1.3,
                "priority": "high"
            },
            {
                "id": 3,
                "title": "Утепление фасада",
                "description": "Дополнительная теплоизоляция наружных стен",
                "investment_rub": 2500000,
                "savings_m3_year": 18000,
                "savings_rub_year": 126000,
                "payback_period_years": 19.8,
                "priority": "medium"
            }
        ],
        "total_investment_rub": 3800000,
        "total_savings_rub_year": 1151000,
        "total_savings_percent": 20.5,
        "co2_reduction_tons_year": 180,
        "engineer_name": "Иванов Иван Петрович",
        "audit_date": "2026-01-05",
        "report_date": "2026-01-15"
    }'::jsonb,
    '2027-12-31'),

-- Отчёт для второго заказа (финальный)
(2, 1, 'final',
    '{
        "executive_summary": "Энергоаудит офисного здания бизнес-центра",
        "energy_consumption": {
            "electricity_kwh_year": 520000,
            "electricity_cost_rub": 2600000,
            "gas_m3_year": 45000,
            "gas_cost_rub": 315000,
            "water_m3_year": 8000,
            "water_cost_rub": 280000,
            "total_cost_rub": 3195000
        },
        "energy_efficiency_class": "C",
        "recommendations": [
            {
                "id": 1,
                "title": "Модернизация системы вентиляции",
                "description": "Установка рекуператоров тепла",
                "investment_rub": 1200000,
                "savings_kwh_year": 65000,
                "savings_rub_year": 325000,
                "payback_period_years": 3.7,
                "priority": "high"
            },
            {
                "id": 2,
                "title": "Автоматизация отопления",
                "description": "Установка погодозависимой автоматики",
                "investment_rub": 350000,
                "savings_m3_year": 9000,
                "savings_rub_year": 63000,
                "payback_period_years": 5.6,
                "priority": "medium"
            }
        ],
        "total_investment_rub": 1550000,
        "total_savings_rub_year": 388000,
        "total_savings_percent": 12.1,
        "co2_reduction_tons_year": 95,
        "engineer_name": "Петрова Мария Александровна",
        "audit_date": "2025-12-10",
        "report_date": "2025-12-20"
    }'::jsonb,
    '2027-06-30'),

-- Отчёт для третьего заказа (черновик)
(3, 1, 'draft',
    '{
        "executive_summary": "Предварительные результаты аудита торгового здания",
        "energy_consumption": {
            "electricity_kwh_year": 180000,
            "electricity_cost_rub": 900000,
            "gas_m3_year": 12000,
            "gas_cost_rub": 84000
        },
        "energy_efficiency_class": "D",
        "recommendations": [
            {
                "id": 1,
                "title": "Замена холодильного оборудования",
                "description": "Установка современных энергоэффективных витрин",
                "investment_rub": 600000,
                "savings_kwh_year": 36000,
                "priority": "high"
            }
        ],
        "engineer_name": "Сидоров Алексей Викторович",
        "audit_date": "2026-01-10"
    }'::jsonb,
    '2026-12-31'),

-- Отчёт для четвертого заказа (черновик, версия 1)
(4, 1, 'draft',
    '{
        "executive_summary": "Начальная версия отчёта для складского комплекса",
        "energy_consumption": {
            "electricity_kwh_year": 320000,
            "gas_m3_year": 30000
        },
        "engineer_name": "Иванов Иван Петрович"
    }'::jsonb,
    '2027-03-31');

-- ============================================
-- FILES - Файлы отчётов
-- ============================================

INSERT INTO reports.files (report_id, file_type, cloud_path) VALUES
-- Файлы для первого отчёта
(1, 'pdf', '/reports/2026/01/order_1_report_v1_final.pdf'),
(1, 'xlsx', '/reports/2026/01/order_1_calculations_v1.xlsx'),
(1, 'archive', '/reports/2026/01/order_1_photos.zip'),

-- Файлы для второго отчёта
(2, 'pdf', '/reports/2025/12/order_2_report_v1_final.pdf'),
(2, 'xlsx', '/reports/2025/12/order_2_calculations_v1.xlsx'),

-- Файлы для третьего отчёта (черновик)
(3, 'pdf', '/reports/2026/01/order_3_report_v1_draft.pdf');

-- ============================================
-- REPORT_HISTORY - История изменений отчётов
-- ============================================

-- После применения миграции 001_alter_report_history.sql
-- эти данные будут автоматически преобразованы в новый формат

INSERT INTO logs.report_history (report_id, user_id, action, diff, created_at) VALUES
-- История первого отчёта (инженер: engineer1@example.com)
(1, (SELECT id FROM auth.users WHERE email = 'engineer1@example.com'), 'Создан черновик отчёта',
    '{"version": 1, "status": "draft"}'::jsonb,
    '2026-01-05 10:30:00'),

(1, (SELECT id FROM auth.users WHERE email = 'engineer1@example.com'), 'Добавлены рекомендации по освещению',
    '{"recommendations_count": {"old": 0, "new": 1}}'::jsonb,
    '2026-01-05 14:20:00'),

(1, (SELECT id FROM auth.users WHERE email = 'engineer1@example.com'), 'Добавлены рекомендации по ЧП и утеплению',
    '{"recommendations_count": {"old": 1, "new": 3}}'::jsonb,
    '2026-01-06 11:15:00'),

(1, (SELECT id FROM auth.users WHERE email = 'engineer1@example.com'), 'Отчёт переведён в финальный статус',
    '{"status": {"old": "draft", "new": "final"}}'::jsonb,
    '2026-01-15 16:45:00'),

-- История второго отчёта (инженер: engineer2@example.com)
(2, (SELECT id FROM auth.users WHERE email = 'engineer2@example.com'), 'Создан черновик отчёта',
    '{"version": 1, "status": "draft"}'::jsonb,
    '2025-12-10 09:00:00'),

(2, (SELECT id FROM auth.users WHERE email = 'engineer2@example.com'), 'Обновлены данные по энергопотреблению',
    '{"energy_consumption": "updated"}'::jsonb,
    '2025-12-12 13:30:00'),

(2, (SELECT id FROM auth.users WHERE email = 'engineer2@example.com'), 'Отчёт утверждён',
    '{"status": {"old": "draft", "new": "final"}}'::jsonb,
    '2025-12-20 17:00:00'),

-- История третьего отчёта (инженер: engineer3@example.com)
(3, (SELECT id FROM auth.users WHERE email = 'engineer3@example.com'), 'Создан черновик отчёта',
    '{"version": 1, "status": "draft"}'::jsonb,
    '2026-01-10 10:00:00'),

(3, (SELECT id FROM auth.users WHERE email = 'engineer3@example.com'), 'Добавлена рекомендация по холодильному оборудованию',
    '{"recommendations_count": {"old": 0, "new": 1}}'::jsonb,
    '2026-01-11 15:30:00'),

-- История четвертого отчёта (инженер: engineer1@example.com)
(4, (SELECT id FROM auth.users WHERE email = 'engineer1@example.com'), 'Создан первоначальный черновик',
    '{"version": 1, "status": "draft"}'::jsonb,
    '2026-01-12 11:45:00');

-- ============================================
-- ПРОВЕРКА ДАННЫХ
-- ============================================

-- Выведем сводку по созданным данным
DO $$
DECLARE
    users_count INTEGER;
    business_count INTEGER;
    orders_count INTEGER;
    reports_count INTEGER;
    files_count INTEGER;
    history_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO users_count FROM auth.users;
    SELECT COUNT(*) INTO business_count FROM core.business;
    SELECT COUNT(*) INTO orders_count FROM core.audit_orders;
    SELECT COUNT(*) INTO reports_count FROM reports.reports;
    SELECT COUNT(*) INTO files_count FROM reports.files;
    SELECT COUNT(*) INTO history_count FROM logs.report_history;

    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Тестовые данные успешно добавлены:';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Пользователей: %', users_count;
    RAISE NOTICE 'Предприятий: %', business_count;
    RAISE NOTICE 'Заказов на аудит: %', orders_count;
    RAISE NOTICE 'Отчётов: %', reports_count;
    RAISE NOTICE 'Файлов: %', files_count;
    RAISE NOTICE 'Записей истории: %', history_count;
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Для входа используйте:';
    RAISE NOTICE 'Email: engineer1@example.com';
    RAISE NOTICE 'Пароль: password123';
    RAISE NOTICE '==============================================';
END $$;
