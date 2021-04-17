#ifndef BBCODE_STREAM_H
#define BBCODE_STREAM_H

#include <iostream>

#include "bbcode/errors.h"

namespace bbcode {

class BaseStream { 
public:

#define VIRTUAL_WRITE_FUNC(type) \
  virtual BaseStream& Write(type const&) { \
    ERROR() << "base stream write func: " #type; \
    return *this; }

#define VIRTUAL_READ_FUNC(type) \
  virtual BaseStream& Read(type *) { \
    ERROR() << "base stream read func: " # type; \
    return *this; }

#define VIRTUAL_RW_FUNC(type) \
  VIRTUAL_READ_FUNC(type) \
  VIRTUAL_WRITE_FUNC(type)

  // arithmeric type
  VIRTUAL_RW_FUNC(bool);
  VIRTUAL_RW_FUNC(char);
  VIRTUAL_RW_FUNC(char16_t);
  VIRTUAL_RW_FUNC(char32_t);
  VIRTUAL_RW_FUNC(wchar_t);
  VIRTUAL_RW_FUNC(signed char);
  VIRTUAL_RW_FUNC(unsigned char);
  VIRTUAL_RW_FUNC(short int);
  VIRTUAL_RW_FUNC(int);
  VIRTUAL_RW_FUNC(long int);
  VIRTUAL_RW_FUNC(long long int);
  VIRTUAL_RW_FUNC(unsigned short int);
  VIRTUAL_RW_FUNC(unsigned int);
  VIRTUAL_RW_FUNC(unsigned long int);
  VIRTUAL_RW_FUNC(unsigned long long int);
  VIRTUAL_RW_FUNC(float);
  VIRTUAL_RW_FUNC(double);
  VIRTUAL_RW_FUNC(long double);

  // string compatiable type
  VIRTUAL_RW_FUNC(std::string);
  VIRTUAL_RW_FUNC(char*);
  VIRTUAL_RW_FUNC(char const*);

  // void type
  VIRTUAL_RW_FUNC(void*);

  // reader function
  bool eof() {
    ERROR() << "abstract eof function";
    return true;
  }
};

class IOStream : public BaseStream {
public:
  IOStream(std::ostream &os = std::cout,
           std::istream &is = std::cin)
    : os_(os), is_(is) {}

#define OS_WRITE_FUNC(type) \
  virtual BaseStream& Write(type const& data) override { \
    os_ << data; return *this; } \

#define IS_READ_FUNC(type) \
  virtual BaseStream& Read(type *data) override { \
    is_ >> *data; return *this; }

#define OS_RW_FUNC(type) \
  IS_READ_FUNC(type) \
  OS_WRITE_FUNC(type)

  // default std::ostream support type
  OS_RW_FUNC(bool);
  OS_RW_FUNC(char);
  OS_WRITE_FUNC(char16_t);
  OS_WRITE_FUNC(char32_t);
  OS_WRITE_FUNC(wchar_t);
  OS_RW_FUNC(signed char);
  OS_RW_FUNC(unsigned char);
  OS_RW_FUNC(short int);
  OS_RW_FUNC(int);
  OS_RW_FUNC(long int);
  OS_RW_FUNC(long long int);
  OS_RW_FUNC(unsigned short int);
  OS_RW_FUNC(unsigned int);
  OS_RW_FUNC(unsigned long int);
  OS_RW_FUNC(unsigned long long int);
  OS_RW_FUNC(float);
  OS_RW_FUNC(double);
  OS_RW_FUNC(long double);

  OS_RW_FUNC(std::string);
  OS_RW_FUNC(char*);
  OS_WRITE_FUNC(char const*);

  // support address printer
  OS_WRITE_FUNC(void*);

private:
  std::ostream &os_;
  std::istream &is_;
};

} // namespace bbcode

#endif // BBCODE_STREAM_H
