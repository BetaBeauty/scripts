/**
 * This header file is used to hack access the private class members, for
 *  sometimes necessarily change the private member state while the library
 *  developers forget to public it.
 *
 * Usage likes this:
 *  HIJACKER(cls, member, type);
 *  HIJACK(&ins, member) = ...
 *
 * More detail codes refer to test source:
 *  tests/test_hihack.cpp
 *
 * Reference via zhihu.com:
 *  https://www.zhihu.com/question/37692782/answer/1212413278
 *
 **/
#ifndef BBCODE_CLS_MEMBER_ACCESS_H
#define BBCODE_CLS_MEMBER_ACCESS_H

#include <type_traits>

namespace bbcode {

template <class T>
using remove_cvref_t = typename std::remove_cv<
  typename std::remove_reference<T>::type>::type;

template <class T>
struct type_identity { using type = T; };
template <class T>
using type_identity_t = typename type_identity<T>::type;

namespace impl
{

template <class T>
struct complete
{
    template <class U>
    static auto test(U*) -> decltype(sizeof(U), std::true_type{});
    static auto test(...) -> std::false_type;
    using type = decltype(test(static_cast<T*>(nullptr)));
};

} // namespace impl

template <class T>
struct is_complete : impl::complete<T>::type {};

} // namespace bbcode

/** Yet another concat implementation. */
#define YA_CAT_IMPL(x, y) x##y
/** Yet another concat. */
#define YA_CAT(x, y) YA_CAT_IMPL(x, y)
/**
 * Init private class member hijacker.
 * @param class_ Class name.
 * @param member Private member to hijack.
 * @param __VA_ARGS__ Member type.
 * @remark All HIJACKERs should appear before any HIJACK.
 */
#define HIJACKER(class_, member, ...) \
    namespace bbcode { namespace hijack { \
    template <class> struct tag_##member; \
    inline auto get(tag_##member<class_>) -> type_identity_t<__VA_ARGS__> class_::*; \
    template <> struct tag_##member<class_> { \
        tag_##member(tag_##member*) {} \
        template <class T, class = typename std::enable_if< \
            !is_complete<tag_##member<T>>::value && \
            std::is_base_of<class_, T>::value>::type> \
        tag_##member(tag_##member<T>*) {} \
    }; \
    template <type_identity_t<__VA_ARGS__> class_::* Ptr> struct YA_CAT(hijack_##member##_, __LINE__) { \
        friend auto get(tag_##member<class_>) -> type_identity_t<__VA_ARGS__> class_::* { return Ptr; } \
    }; \
    template struct YA_CAT(hijack_##member##_, __LINE__)<&class_::member>; \
    }}
/**
 * Hijack private class member.
 * @param ptr Pointer to class instance.
 * @param member Private member to hijack.
 * @remark All HIJACKs should appear after any HIJACKER.
 */
#define HIJACK(ptr, member) \
    ((ptr)->*bbcode::hijack::get( \
        static_cast<std::add_pointer<bbcode::hijack::tag_##member< \
            bbcode::remove_cvref_t<decltype(*ptr)>>>::type>(nullptr)))

#endif // BBCODE_CLS_MEMBER_ACCESS_H
