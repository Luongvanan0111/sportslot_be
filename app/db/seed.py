from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.security import hash_password
from app.models.profile import Profile
from app.models.user import User
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.utils.enums import RoleEnum, UserStatus
from app.utils.text import normalize_text
from app.utils.timezone import now_vn

# Ma trận phân quyền 16 permissions hạt nhân
_PERMISSION_GRANTS: dict[str, list[RoleEnum]] = {
    # Nhóm Role
    "role:list": [],
    "role:create": [],
    "role:update": [],
    "role:delete": [],
    # Nhóm Permission
    "permission:list": [],
    "permission:create": [],
    "permission:update": [],
    "permission:delete": [],
    # Nhóm Term
    "term:list": [],
    "term:create": [],
    "term:update": [],
    "term:delete": [],
    # Nhóm User
    "user:list": [],
    "user:create": [],
    "user:update": [],
    "user:delete": [],
}


async def seed_all_data(db: AsyncSession) -> None:
    """Khởi tạo dữ liệu mẫu ban đầu: Roles, Permissions, Admin account & Profile (Idempotent)."""
    logger.info("[SEED] Bắt đầu quá trình seed dữ liệu hệ thống...")
    role_repo = RoleRepository(db)
    user_repo = UserRepository(db)

    # 1. Seed danh mục 3 Roles
    role_entities: dict[str, int] = {}
    for role_enum in RoleEnum:
        role_name = role_enum.value
        existing_role = await role_repo.get_by_name(role_name)
        if not existing_role:
            created_role = await role_repo.create_role(
                name=role_name,
                description=f"System role: {role_name}",
            )
            role_entities[role_name] = created_role.id
            logger.info(f"  [SEED] Đã tạo role: {role_name}")
        else:
            role_entities[role_name] = existing_role.id

    admin_role_id = role_entities[RoleEnum.ADMIN.value]

    # 2. Seed danh mục 16 Permissions kỹ thuật và gán quyền cho Admin
    for perm_code, assigned_roles in _PERMISSION_GRANTS.items():
        existing_perm = await role_repo.get_permission_by_code(perm_code)
        if not existing_perm:
            perm = await role_repo.create_permission(
                code=perm_code,
                description=f"Permission for {perm_code}",
            )
            perm_id = perm.id
            logger.info(f"  [SEED] Đã tạo permission: {perm_code}")
        else:
            perm_id = existing_perm.id

        # Admin luôn nhận toàn bộ 100% permissions
        await role_repo.assign_permission_to_role(admin_role_id, perm_id)

        # Gán cho các roles khác nếu được định nghĩa trong ma trận
        for r_enum in assigned_roles:
            r_id = role_entities.get(r_enum.value)
            if r_id:
                await role_repo.assign_permission_to_role(r_id, perm_id)

    # 3. Seed tài khoản Admin mặc định & Profile nếu có cấu hình trong .env
    if not settings.admin_email or not settings.admin_password:
        logger.warning(
            "  [SEED] Bỏ qua seed tài khoản Admin: ADMIN_EMAIL hoặc ADMIN_PASSWORD chưa được cấu hình trong .env"
        )
        await db.commit()
        logger.info("[SEED] Hoàn thành seed dữ liệu hệ thống (Roles & Permissions) thành công!")
        return

    admin_user = await user_repo.get_by_identifier(settings.admin_email)
    if not admin_user:
        admin_user = await user_repo.get_by_identifier(settings.admin_username)

    if not admin_user:
        hashed_pwd = hash_password(settings.admin_password)
        admin_user = User(
            email=settings.admin_email.lower(),
            username=settings.admin_username.lower(),
            password_hash=hashed_pwd,
            status=UserStatus.ACTIVATED.value,
            verified_at=now_vn(),
            failed_login_attempts=0,
        )
        await user_repo.create(admin_user)

        # Gán vai trò admin
        await role_repo.assign_role_to_user(admin_user.id, admin_role_id)

        # Tạo hồ sơ cá nhân (Profile) gắn liền với Admin
        admin_profile = Profile(
            user_id=admin_user.id,
            full_name=settings.admin_full_name,
            full_name_no_uni=normalize_text(settings.admin_full_name),
        )
        db.add(admin_profile)
        await db.flush()
        logger.info(
            f"  [SEED] Đã tạo tài khoản Admin mặc định: {settings.admin_email} ({settings.admin_username})"
        )
    else:
        # Đảm bảo admin có vai trò admin
        await role_repo.assign_role_to_user(admin_user.id, admin_role_id)

    await db.commit()
    logger.info("[SEED] Hoàn thành seed dữ liệu hệ thống thành công!")
